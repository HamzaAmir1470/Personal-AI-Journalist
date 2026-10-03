import asyncio
import os
from typing import Dict, List

from aiolimiter import AsyncLimiter
from dotenv import load_dotenv

from utils import (
    clean_html_to_text,
    extract_headlines,
    generate_news_urls_to_scrape,
    scrape_with_scraperapi,
    summarize_with_mistral_news_script,
)

load_dotenv()


class NewsScraper:
    _rate_limiter = AsyncLimiter(5, 1)  # 5 requests per second

    async def scrape_news(self, topics: List[str]) -> Dict[str, Dict[str, str]]:
        """Scrape and analyze news articles for given topics."""
        results = {}

        for topic in topics:
            async with self._rate_limiter:
                try:
                    urls = generate_news_urls_to_scrape([topic])
                    search_html = scrape_with_scraperapi(urls[topic])
                    clean_text = clean_html_to_text(search_html)
                    headlines = extract_headlines(clean_text)
                    summary = summarize_with_mistral_news_script(
                        api_key=os.getenv("MISTRAL_API_KEY"),
                        headlines=headlines,
                    )
                    results[topic] = summary
                except Exception as e:
                    results[topic] = f"Error scraping topic '{topic}': {str(e)}"

                await asyncio.sleep(1)

        return {"news_analysis": results}
