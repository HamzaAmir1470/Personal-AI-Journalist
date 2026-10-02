from urllib.parse import quote_plus
import os

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


def scrape_with_brightdata(url: str) -> str:
    """Scrape & URL using BrightData"""
    headers = {
        "Authorization": f"Bearer {os.getenv('SCRAPER_API_URL')}",
        "Content-Type": "application/json",
    }
    payload = {
        "zone": os.getenv("BRIGHTDATA_WEB_UNLOCKER_ZONE"),
        "urt": url,
        "format": "raw",
    }

    try:
        response = requests.post("https://api.brightdata.com/request", json=payload, headers=headers)
        response. raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"BrightData error: {str(e)}")