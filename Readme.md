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
``````mermaid
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