import os
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mistralai import ChatMistralAI
from datetime import datetime
from elevenlabs import ElevenLabs

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



def summarize_with_mistral_news_script(api_key: str, headlines: str) -> str:
    """
    Summarize multiple news headlines into a TTS-friendly broadcast news script
    using Mistral AI model via langchain_mistralai.
    """
    system_prompt = """
    You are broadcast_news_writer, a professional virtual news reporter. Generate natural, TTS-ready news reports using available sources:

    For each topic, STRUCTURE BASED ON AVAILABLE DATA:
    1. If news exists: "According to official reports..." + summary
    2. If Reddit exists: "Online discussions on Reddit reveal..." + summary
    3. If both exist: Present news first, then Reddit reactions
    4. If neither exists: Skip the topic (shouldn't happen)

    Formatting rules:
    - ALWAYS start directly with the content, NO INTRODUCTIONS
    - Keep audio length 60-120 seconds per topic
    - Use natural speech transitions like "Meanwhile, online discussions..." 
    - Incorporate 1-2 short quotes from Reddit when available
    - Maintain neutral tone but highlight key sentiments
    - End with "To wrap up this segment..." summary

    Write in full paragraphs optimized for speech synthesis. Avoid markdown.
    """
    try:
        llm = ChatMistralAI(
            model="mistral-small-latest",
            api_key=api_key,
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

def text_to_audio_elevenlabs_sdk(
    text: str,
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb",
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
    output_dir: str = "audio",
    api_key: str = None
) -> str:
    """
    Converts text to speech using ElevenLabs SDK and saves it to audio/ directory.

    Returns:
        str: Path to the saved audio file.
    """
    try:
        api_key = api_key or os.getenv("ELEVEN_API_KEY")
        if not api_key:
            raise ValueError("ElevenLabs API key is required.")

        # Initialize client
        client = ElevenLabs(api_key=api_key)

        # Get the audio generator
        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format
        )

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate unique filename
        filename = f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        filepath = os.path.join(output_dir, filename)

        # Write audio chunks to file
        with open(filepath, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        return filepath

    except Exception as e:
        raise e

from pathlib import Path
from gtts import gTTS
AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(exist_ok=True)  # Create directory if it doesn't exist
def tts_to_audio(text: str, language: str = 'en') -> str:
    """
    Convert text to speech using gTTS (Google Text-to-Speech) and save to file.
    
    Args:
        text: Input text to convert
        language: Language code (default: 'en')
    
    Returns:
        str: Path to saved audio file
    
    Example:
        tts_to_audio("Hello world", "en")
    """
    try:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = AUDIO_DIR / f"tts_{timestamp}.mp3"
        
        # Create TTS object and save
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(str(filename))
        
        return str(filename)
    except Exception as e:
        print(f"gTTS Error: {str(e)}")
        return None