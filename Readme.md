```mermaid
erDiagram
    USER ||--o{ NEWS_REQUEST : places
    NEWS_REQUEST ||--|{ REQUEST_TOPIC : contains
    NEWS_REQUEST ||--o| NEWS_ANALYSIS : generates
    NEWS_REQUEST ||--o| REDDIT_ANALYSIS : generates
    NEWS_REQUEST ||--o| BROADCAST_SCRIPT : produces
    BROADCAST_SCRIPT ||--o| AUDIO_OUTPUT : synthesizes

    USER {
        string user_id PK
        string session_id
        string ip_address
    }

    NEWS_REQUEST {
        string request_id PK
        string source_type "news | reddit | both"
        datetime created_at
        string status "pending | processing | completed | failed"
    }

    REQUEST_TOPIC {
        string topic_id PK
        string request_id FK
        string topic_name "e.g., AI, Cricket, Tech"
    }

    NEWS_ANALYSIS {
        string analysis_id PK
        string request_id FK
        string topic_name
        text raw_html
        text cleaned_text
        text extracted_headlines
        text news_summary
        string scraper_status
    }

    REDDIT_ANALYSIS {
        string analysis_id PK
        string request_id FK
        string topic_name
        text reddit_summary
        string sentiment "positive | neutral | negative"
        text key_opinions
        datetime cutoff_date
    }

    BROADCAST_SCRIPT {
        string script_id PK
        string request_id FK
        text full_script_text
        string llm_model "mistral-small-latest"
        int word_count
        float estimated_duration_seconds
        datetime generated_at
    }

    AUDIO_OUTPUT {
        string audio_id PK
        string script_id FK
        string file_path "audio/tts_timestamp.mp3"
        string tts_provider "ElevenLabs | gTTS"
        string voice_id "JBFqnCBsd6RMkjVDRZzb"
        string output_format "mp3_44100_128"
        int file_size_bytes
        datetime created_at
    }
```
## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub and create an app at
   [share.streamlit.io](https://share.streamlit.io/).
2. Select `streamlit_app.py` as the main file.
3. Add these secrets in **App settings > Secrets**:

   ```toml
   MISTRAL_API_KEY = "your-mistral-key"
   SCRAPER_API_KEY = "your-scraperapi-key"
   ELEVEN_API_KEY = "your-elevenlabs-key"
   ```

The app runs the news, summarization, and audio pipeline in the Streamlit
process, so it does not require a localhost FastAPI server. For a separately
deployed FastAPI service, set `BACKEND_URL` as an additional secret; the UI
will use that service instead.

For local development, install dependencies with `pip install -r requirements.txt`
and run:

```bash
streamlit run streamlit_app.py
```

### About the `pywin32` installation error

Do not deploy `Pipfile.lock` directly to Streamlit Community Cloud. That lock
file was generated on Windows and contains `pywin32==312`, a Windows-only
package. Streamlit Community Cloud runs Linux, so pip correctly reports that
there is no compatible `pywin32` distribution for that environment.

Use the platform-neutral `requirements.txt` file instead. The `dotenv`
Pipfile entry is represented as `python-dotenv`, which is the maintained
package that provides the `dotenv` import used by this project. Streamlit's
dependency resolver will install Linux-compatible transitive dependencies.
