import asyncio
from datetime import datetime, timedelta
import os
import sys
from typing import Dict, List

from aiolimiter import AsyncLimiter
from dotenv import load_dotenv
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mistralai import ChatMistralAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

load_dotenv()

# Setup Stdio parameters for the ScraperAPI MCP Server
server_params = StdioServerParameters(
    command=sys.executable,
    args=["-m", "scraperapi_mcp_server"],
    env={
        **os.environ,
        "API_KEY": os.getenv("SCRAPER_API_KEY", ""),
    },
)

model = ChatMistralAI(
    model="open-mistral-7b",
    api_key=os.getenv("MISTRAL_API_KEY"),
    temperature=0.4,
)


class MCPOverloadedError(Exception):
    pass


mcp_limiter = AsyncLimiter(1, 15)
two_weeks_ago = datetime.today() - timedelta(days=14)
two_weeks_ago_str = two_weeks_ago.strftime("%Y-%m-%d")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=15, max=60),
    retry=retry_if_exception_type(MCPOverloadedError),
    reraise=True,
)
async def process_topic(agent, topic: str) -> str:
    """Analyze a single Reddit topic using the configured agent."""
    async with mcp_limiter:
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a Reddit analysis expert. Use available tools to:\n"
                    f"1. Find top 2 posts about the given topic BUT only after {two_weeks_ago_str}, "
                    f"NOTHING before this date strictly!\n"
                    f"2. Analyze their content and sentiment\n"
                    f"3. Create a summary of discussions and overall sentiment"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Analyze Reddit posts about '{topic}'.\n"
                    f"Provide a comprehensive summary including:\n"
                    f"- Main discussion points\n"
                    f"- Key opinions expressed\n"
                    f"- Any notable trends or patterns\n"
                    f"- Summarize the overall narrative, discussion points and also quote interesting comments without mentioning names\n"
                    f"- Overall sentiment (positive/neutral/negative)"
                ),
            },
        ]

        try:
            response = await agent.ainvoke({"messages": messages})
            return response["messages"][-1].content
        except Exception as e:
            if "Overloaded" in str(e):
                raise MCPOverloadedError("Service overloaded")
            raise e


async def scrape_reddit_topics(
    topics: List[str],
) -> Dict[str, Dict[str, str]]:
    """Process a list of topics via MCP agent and return Reddit analysis results."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)

            reddit_results = {}
            for topic in topics:
                summary = await process_topic(agent, topic)
                reddit_results[topic] = summary
                await asyncio.sleep(5)  # Maintain rate limiting

            return {"reddit_analysis": reddit_results}
