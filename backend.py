import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response

from models import NewsRequest
from news_scrapper import NewsScraper
from utils import generate_broadcast_news, text_to_audio_elevenlabs_sdk

app = FastAPI()
load_dotenv()


@app.post("/generate-news-audio")
async def generate_news_audio(request: NewsRequest):
    try:
        results = {}

        # All requests ("news", "reddit", or "both") strictly route through NewsScraper
        news_scraper = NewsScraper()
        results["news"] = await news_scraper.scrape_news(request.topics)

        news_data = results.get("news", {})
        reddit_data = {}  # Set to empty dict as reddit_scrapper is disabled

        news_summary = generate_broadcast_news(
            api_key=os.getenv("MISTRAL_API_KEY"),
            news_data=news_data,
            reddit_data=reddit_data,
            topics=request.topics,
        )

        audio_path = text_to_audio_elevenlabs_sdk(
            text=news_summary,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            output_dir="audio",
        )

        if audio_path and Path(audio_path).exists():
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": "attachment; filename=news-summary.mp3"
                },
            )

        raise HTTPException(status_code=500, detail="Audio file creation failed.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend:app", host="127.0.0.1", port=1234, reload=True)
