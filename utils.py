import os
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mistralai import ChatMistralAI


def generate_valid_news_url(keyword: str) -> str:
    """
    Generate a Google News search URL for a keyword

    Args:
        keyword: Search term to use in the news search

    Returns:
        str: Constructed Google News search URL
    """
    q = quote_plus(keyword)
    return f"https://news.google.com/search?q={q}&tbs=sbd:1"


def scrape_with_scraperapi(url: str) -> str:
    """Scrape a URL using ScraperAPI"""
    api_key = os.getenv("SCRAPER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, detail="SCRAPER_API_KEY environment variable missing"
        )

    params = {"api_key": api_key, "url": url}

    try:
        response = requests.get(
            "https://api.scraperapi.com/", params=params, timeout=60
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"ScraperAPI error: {str(e)}")


def clean_html_to_text(html_content: str) -> str:
    """Clean HTML content to plain text"""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n")
    return text.strip()


def extract_headlines(cleaned_text: str) -> str:
    """
    Extract and concatenate headlines from cleaned news text content.

    Args:
        cleaned_text: Raw text from news page after HTML cleaning

    Returns:
        str: Combined headlines separated by newlines
    """
    headlines = []
    current_block = []

    # Split text into lines and remove empty lines
    lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]

    # Process lines to find headline blocks
    for line in lines:
        if line == "More":
            if current_block:
                # First line of block is headline
                headlines.append(current_block[0])
                current_block = []

            current_block.append(line)
        else:
            current_block.append(line)

    # Add any remaining block at end of text
    if current_block:
        headlines.append(current_block[0])

    return "\n".join(headlines)


def summarize_with_mistral_news_script(headlines: str) -> str:
    """
    Summarize multiple news headlines into a TTS-friendly broadcast news script
    using Mistral AI model via langchain_mistralai.
    """
    system_prompt = """
    You are my personal news editor and scriptwriter for a news podcast. Your job is to turn raw headlines into a clean, professional, and TTS-friendly news script. 

    The final output will be read aloud by a news anchor or text-to-speech engine. So:
    - Do not include any special characters, emojis, formatting symbols, or markdown.
    - Do not add any preamble or framing like "Here's your summary" or "Let me explain".
    - Write in full, clear, spoken-language paragraphs.
    - Keep the tone formal, professional, and broadcast-style - just like a real TV news script.
    - Focus on the most important headlines and turn them into short, informative news segments that sound natural.
    - Start right away with the actual script, using transitions between topics if needed.

    Remember: Your only output should be a clean script that is ready to be read out loud.
    """
    try:
        llm = ChatMistralAI(
            model="mistral-small-latest",
            api_key=os.getenv("MISTRAL_API_KEY"),
            temperature=0.4,
            max_tokens=1000,
        )

        # Invoke Mistral with system + user prompt
        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=headlines),
            ]
        )
        return response.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mistral error: {str(e)}")


def generate_news_urls_to_scrape(list_of_keywords):
    valid_urls_dict = {}
    for keyword in list_of_keywords:
        valid_urls_dict[keyword] = generate_valid_news_url(keyword)

    return valid_urls_dict
