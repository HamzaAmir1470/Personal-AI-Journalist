from fastapi import FastAPI, HTTPException, Response, File
from dotenv import load_dotenv

from models import NewsRequest

app = FastAPI()
load_dotenv()

@app.post("/generate-news-audio")
async def generate_news_audio(request: NewsRequest):
    try:
        results={}
        
        if request.source_type in ["news", "both"]:
            #scrape news
            results["news"] = {"news_scrapped": "This is from google news"}
        
        if request.source_type in ["reddit", "both"]:
            #scrape reddit
            results["reddit"] = {"reddit_scraped": "This is from reddit"}

        news_data = results.get("news", {})
        reddit_data = results.get("reddit", {})
        
        #setup LLM summarizer
        
        news_summary = my_summary_function(news_data, reddit_data)
        
        #convert summary to audio
        
        audio_path = convert_text_to_audio(news_summary)
        
        
        if audio_path:
            
            return response, headers, etc
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))