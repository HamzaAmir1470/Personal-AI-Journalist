import html
import asyncio
import os
from pathlib import Path
from typing import Callable, Optional

import requests
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from news_scrapper import NewsScraper
from utils import generate_broadcast_news, text_to_audio_elevenlabs_sdk


def load_streamlit_secrets():
    """Expose Streamlit Cloud secrets to the existing service clients."""
    try:
        for name in ("MISTRAL_API_KEY", "SCRAPER_API_KEY", "ELEVEN_API_KEY"):
            if not os.getenv(name) and name in st.secrets:
                os.environ[name] = str(st.secrets[name])
    except StreamlitSecretNotFoundError:
        # Local development can use a .env file instead of Streamlit secrets.
        return


load_streamlit_secrets()
BACKEND_URL = os.getenv("BACKEND_URL", "").rstrip("/")

# ---------------------------------------------------------------------------
# Styling & Forced Contrast Theme Setup
# Fixed input field visibility & button contrast
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800&display=swap');

:root {
  --ink: #142036;
  --mute: #5B6780;
  --line: #DCE2EE;
  --acc: #3A3FD8;
  --acc-2: #6C70FF;
  --hl: #FFD166;
  --side: #0A0A0F;
  --side-2: #12162A;
  --side-line: #232946;
  --side-ink: #F4F6FF;
}

/* ---------- Base Layout ---------- */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background-color: #FFFFFF !important;
  color: var(--ink) !important;
  color-scheme: light !important;
}

.stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label, .stApp input,
.stApp button, .stApp li, div[data-baseweb="popover"] {
  font-family: 'Bricolage Grotesque', system-ui, -apple-system, sans-serif !important;
}

#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 880px; padding-top: 5.5rem; padding-bottom: 4rem; }

/* ---------- Top Bar Header ---------- */
header[data-testid="stHeader"] {
  background-color: #0A0A0F !important;
  border-bottom: 1px solid var(--side-line);
  height: 3.5rem;
}

header[data-testid="stHeader"]::after {
  content: "";
  position: absolute; left: 0; right: 0; bottom: -1px; height: 3px;
  background: linear-gradient(90deg, #142036, #2B31B8, #3A3FD8, #6C70FF, #FFD166, #3A3FD8, #142036);
  background-size: 300% 100%;
  animation: edgeShift 10s linear infinite;
}

/* Force Streamlit top header buttons, icons, and menus to appear white */
header[data-testid="stHeader"] *, 
[data-testid="stToolbar"] *, 
header[data-testid="stHeader"] button, 
header[data-testid="stHeader"] svg {
  color: #FFFFFF !important;
  fill: #FFFFFF !important;
  stroke: #FFFFFF !important;
}

/* ---------- Hero Banner ---------- */
.hero {
  position: relative; overflow: hidden; border-radius: 24px;
  padding: 34px 36px 30px;
  background: linear-gradient(120deg, #142036, #2B31B8, #3A3FD8, #142036);
  background-size: 300% 300%;
  animation: heroShift 14s ease infinite, riseIn .7s cubic-bezier(.2,.8,.2,1) both;
  box-shadow: 0 18px 40px -18px rgba(58,63,216,.55);
}
.hero h1 { margin: 0 0 6px; padding: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.05; color: #FFFFFF !important; }
.hero p { margin: 0; max-width: 48ch; font-size: 1.02rem; color: rgba(255,255,255,.85) !important; }
.flow { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.flow span { color: #FFFFFF !important; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.24); border-radius: 999px; padding: 4px 13px; font-size: .84rem; }

.wave { position: absolute; right: 30px; top: 30px; display: flex; align-items: center; gap: 4px; height: 56px; }
.wave i { display: block; width: 5px; height: 100%; border-radius: 3px; background: var(--hl); animation: bar 1.2s ease-in-out infinite; }
.wave i:nth-child(1){ animation-delay: -1.1s } .wave i:nth-child(2){ animation-delay: -.9s }
.wave i:nth-child(3){ animation-delay: -.7s } .wave i:nth-child(4){ animation-delay: -.5s }
.wave i:nth-child(5){ animation-delay: -.3s } .wave i:nth-child(6){ animation-delay: -.1s }
.wave i:nth-child(7){ animation-delay: -.6s }

@keyframes bar { 0%,100% { transform: scaleY(.25); } 50% { transform: scaleY(1); } }
@keyframes heroShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
@keyframes edgeShift { from { background-position: 0% 0; } to { background-position: 300% 0; } }
@keyframes riseIn { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
@keyframes popIn { from { opacity: 0; transform: scale(.94) translateX(-6px); } to { opacity: 1; transform: scale(1) translateX(0); } }

/* ---------- Section Labels ---------- */
.section { display: flex; align-items: center; gap: 12px; margin: 30px 0 10px; font-weight: 600; font-size: 1.05rem; color: var(--ink) !important; }
.section::after { content: ""; flex: 1; height: 1px; background: var(--line); }
.hint { color: var(--mute) !important; font-size: .9rem; margin: -2px 0 10px; }

/* ---------- Input Controls ---------- */
.stTextInput label p { color: var(--ink) !important; font-weight: 600; }
.stTextInput div[data-baseweb="input"] {
  background-color: #FFFFFF !important;
  border: 1.5px solid var(--line) !important;
  border-radius: 14px !important;
}
.stTextInput div[data-baseweb="input"]:focus-within {
  border-color: var(--acc) !important;
  box-shadow: 0 0 0 4px rgba(58,63,216,.14) !important;
}
.stTextInput input {
  background-color: #FFFFFF !important;
  color: #142036 !important;
  -webkit-text-fill-color: #142036 !important;
  padding: 12px 14px !important;
  font-weight: 500 !important;
}
.stTextInput input::placeholder {
  color: #8A94A8 !important;
  -webkit-text-fill-color: #8A94A8 !important;
  opacity: 1 !important;
}

/* ---------- Buttons & Remove Button Styles (EXPLICIT FIX) ---------- */
.stButton > button, 
.stFormSubmitButton > button, 
.stDownloadButton > button,
div[data-testid="column"] button,
button[kind="secondary"] {
  background-color: #FFFFFF !important;
  background: #FFFFFF !important;
  color: #142036 !important;
  border: 1.5px solid var(--line) !important;
  border-radius: 14px !important;
  font-weight: 600 !important;
  padding: .6rem 1.1rem !important;
  transition: all 0.2s ease-in-out !important;
}

.stButton > button p, 
.stFormSubmitButton > button p, 
.stDownloadButton > button p,
div[data-testid="column"] button p,
button[kind="secondary"] p {
  color: #142036 !important;
  -webkit-text-fill-color: #142036 !important;
  transition: color 0.2s ease-in-out !important;
}

/* Hover & Focus state for Remove & Secondary buttons */
.stButton > button:hover:not(:disabled),
.stFormSubmitButton > button:hover:not(:disabled),
.stDownloadButton > button:hover:not(:disabled),
div[data-testid="column"] button:hover:not(:disabled),
button[kind="secondary"]:hover:not(:disabled) {
  border-color: var(--acc) !important;
  color: var(--acc) !important;
  background-color: #F6F8FD !important;
  background: #F6F8FD !important;
  box-shadow: 0 2px 8px rgba(58,63,216,0.08) !important;
}

.stButton > button:hover:not(:disabled) p,
.stFormSubmitButton > button:hover:not(:disabled) p,
.stDownloadButton > button:hover:not(:disabled) p,
div[data-testid="column"] button:hover:not(:disabled) p,
button[kind="secondary"]:hover:not(:disabled) p {
  color: var(--acc) !important;
  -webkit-text-fill-color: var(--acc) !important;
}

/* Primary Accent Button Style (Generate Summary / Download) */
.stButton > button[kind="primary"], 
.stDownloadButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--acc), var(--acc-2)) !important;
  color: #FFFFFF !important;
  border: 0 !important;
}
.stButton > button[kind="primary"] p, 
.stDownloadButton > button[kind="primary"] p {
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
}

.stButton > button[kind="primary"]:hover:not(:disabled),
.stDownloadButton > button[kind="primary"]:hover:not(:disabled) {
  opacity: 0.92 !important;
  background: linear-gradient(135deg, var(--acc), var(--acc-2)) !important;
  color: #FFFFFF !important;
}

/* ---------- Topic Item Component ---------- */
.topic-card {
  display: flex; align-items: center; justify-content: space-between;
  background: #F6F8FD; border: 1px solid var(--line); border-radius: 14px;
  padding: 10px 16px; margin-bottom: 8px;
  animation: popIn .35s cubic-bezier(.2,.8,.2,1) both;
}
.topic-left { display: flex; align-items: center; gap: 12px; }
.topic-num { width: 26px; height: 26px; border-radius: 50%; display: grid; place-items: center; background: var(--acc); color: #FFFFFF; font-size: .82rem; font-weight: 600; }
.topic-text { font-weight: 600; color: var(--ink); font-size: 0.98rem; }
.source-badge {
  background: #E2E8F0; color: #334155; font-size: 0.78rem; font-weight: 600;
  padding: 3px 10px; border-radius: 999px; border: 1px solid #CBD5E1;
}

/* ---------- Generation Trace ---------- */
.generation-trace {
  margin: 18px 0 20px;
  padding: 18px 20px;
  background: #F8FAFF;
  border: 1px solid #C9D2E5;
  border-radius: 16px;
  box-shadow: 0 8px 22px rgba(20, 32, 54, .08);
}
.generation-trace-title {
  color: #142036 !important;
  font-size: .96rem;
  font-weight: 800;
  margin-bottom: 12px;
}
.trace-step {
  display: flex;
  align-items: center;
  gap: 11px;
  min-height: 34px;
  color: #53617A !important;
  font-size: .92rem;
  font-weight: 600;
}
.trace-step.active { color: #252B9B !important; }
.trace-step.done { color: #147A55 !important; }
.trace-icon {
  display: grid;
  place-items: center;
  width: 23px;
  height: 23px;
  border-radius: 50%;
  background: #D9E1F2;
  color: #53617A !important;
  font-size: .78rem;
  font-weight: 800;
}
.trace-step.active .trace-icon {
  background: #3A3FD8;
  color: #FFFFFF !important;
  box-shadow: 0 0 0 4px rgba(58, 63, 216, .16);
}
.trace-step.done .trace-icon {
  background: #14845D;
  color: #FFFFFF !important;
}
.trace-line {
  height: 12px;
  margin-left: 11px;
  border-left: 2px solid #D9E1F2;
}

/* Streamlit status/spinner contrast overrides */
[data-testid="stStatusWidget"],
[data-testid="stStatusWidget"] summary,
[data-testid="stStatusWidget"] div,
[data-testid="stSpinner"] {
  color: #142036 !important;
}
[data-testid="stStatusWidget"] {
  background: #F8FAFF !important;
  border: 1px solid #C9D2E5 !important;
  border-radius: 16px !important;
}

/* ---------- Dark Sidebar ---------- */
section[data-testid="stSidebar"] {
  background-color: var(--side) !important;
  border-right: 1px solid var(--side-line);
}
section[data-testid="stSidebar"] * { color: var(--side-ink) !important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  background-color: var(--side-2) !important; border: 1.5px solid var(--side-line) !important; border-radius: 14px;
}
section[data-testid="stSidebar"] input[role="combobox"] {
  color: #142036 !important;
  -webkit-text-fill-color: #142036 !important;
  background-color: transparent !important;
}
section[data-testid="stSidebar"] button[aria-label="Open"] svg {
  fill: #142036 !important;
  stroke: #142036 !important;
}
div[data-baseweb="popover"] > div, div[data-baseweb="popover"] ul {
  background-color: var(--side-2) !important; border: 1px solid var(--side-line) !important;
}
div[data-baseweb="popover"] li { color: #F4F6FF !important; }
div[data-baseweb="popover"] li:hover { background-color: #252B5A !important; }
</style>
"""

HERO_HTML = (
    '<div class="hero">'
    '<div class="wave"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>'
    "<h1>Personal AI Journalist</h1>"
    "<p>Specify topics along with your preferred news sources to generate an audio news briefing.</p>"
    '<div class="flow"><span>Reddit</span><span>Google News</span><span>Summary</span><span>Audio Synthesis</span></div>'
    "</div>"
)


def section(title, hint=None):
    """Render a styled section heading."""
    st.markdown(f'<div class="section">{title}</div>', unsafe_allow_html=True)
    if hint:
        st.markdown(f'<div class="hint">{hint}</div>', unsafe_allow_html=True)


def handle_api_error(response):
    """Handle API error responses gracefully."""
    try:
        error_detail = response.json().get("detail", "Unknown error")
        st.error(f"API Error ({response.status_code}): {error_detail}")
    except ValueError:
        st.error(f"Unexpected API Response: {response.text}")


def generate_audio_briefing(
    topics: list[str], on_progress: Optional[Callable[[str], None]] = None
):
    """Generate audio locally, or use a separately deployed backend when configured."""
    def report(stage: str) -> None:
        if on_progress:
            on_progress(stage)

    if BACKEND_URL:
        report("scraping")
        response = requests.post(
            f"{BACKEND_URL}/generate-news-audio",
            json={"topics": topics, "source_type": "news"},
            timeout=300,
        )
        if response.status_code != 200:
            handle_api_error(response)
            return None
        report("audio")
        return response.content

    missing_keys = [
        name
        for name in ("SCRAPER_API_KEY", "MISTRAL_API_KEY", "ELEVEN_API_KEY")
        if not os.getenv(name)
    ]
    if missing_keys:
        raise RuntimeError(
            "Missing required secrets: "
            + ", ".join(missing_keys)
            + ". Add them to Streamlit Cloud app settings."
        )

    report("scraping")
    news_data = asyncio.run(NewsScraper().scrape_news(topics))
    report("summary")
    news_summary = generate_broadcast_news(
        api_key=os.environ["MISTRAL_API_KEY"],
        news_data=news_data,
        reddit_data={},
        topics=topics,
    )
    report("audio")
    audio_path = text_to_audio_elevenlabs_sdk(
        text=news_summary,
        output_dir="audio",
        api_key=os.environ["ELEVEN_API_KEY"],
    )
    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise RuntimeError("Audio file creation failed.")
    return audio_file.read_bytes()


def render_generation_trace(active_stage: str) -> None:
    """Render the high-contrast progress trace for the current generation stage."""
    stages = [
        ("scraping", "Scraping data", "Collecting the latest stories from your selected sources"),
        ("summary", "Generating summary", "Turning the stories into a broadcast-ready script"),
        ("audio", "Generating audio", "Synthesizing your personalized news briefing"),
    ]
    active_index = next(
        (index for index, (key, _, _) in enumerate(stages) if key == active_stage),
        0,
    )
    parts = ['<div class="generation-trace"><div class="generation-trace-title">Building your briefing</div>']
    for index, (key, title, description) in enumerate(stages):
        state = "done" if index < active_index else "active" if index == active_index else ""
        icon = "✓" if state == "done" else "•" if state == "active" else str(index + 1)
        parts.append(
            f'<div class="trace-step {state}"><span class="trace-icon">{icon}</span>'
            f"<span>{title} <small>— {description}</small></span></div>"
        )
        if index < len(stages) - 1:
            parts.append('<div class="trace-line"></div>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Personal AI Journalist",
        page_icon="🎙️",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(HERO_HTML, unsafe_allow_html=True)

    # Initialize state for structured topic entries
    if "topic_list" not in st.session_state:
        st.session_state.topic_list = []

    # Sidebar settings
    with st.sidebar:
        st.header("Settings")
        source_type = st.selectbox(
            "Target Data Sources",
            options=["both", "news", "reddit"],
            format_func=lambda x: {
                "both": "Reddit + Google News",
                "news": "Google News",
                "reddit": "Reddit",
            }[x],
        )

    SOURCE_LABELS = {
        "both": "Reddit + Google News",
        "news": "Google News",
        "reddit": "Reddit",
    }

    # Topic Management
    section("Topic Management", "Add up to 3 topics to include in your audio briefing.")

    with st.form("add_topic_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 2])
        with col1:
            new_topic = st.text_input(
                "Topic name",
                placeholder="e.g. Artificial Intelligence, Stock Markets",
                label_visibility="collapsed",
            )
        with col2:
            add_disabled = len(st.session_state.topic_list) >= 3
            submitted = st.form_submit_button(
                "Add topic", disabled=add_disabled, use_container_width=True
            )

        if submitted and new_topic.strip():
            if len(st.session_state.topic_list) < 3:
                st.session_state.topic_list.append(
                    {"name": new_topic.strip(), "source": source_type}
                )
                st.rerun()

    # Display Selected Topics
    if st.session_state.topic_list:
        section("Selected Topics")
        for i, item in enumerate(st.session_state.topic_list):
            cols = st.columns([5, 1])
            with cols[0]:
                st.markdown(
                    f'<div class="topic-card">'
                    f'  <div class="topic-left">'
                    f'    <span class="topic-num">{i+1}</span>'
                    f'    <span class="topic-text">{html.escape(item["name"])}</span>'
                    f"  </div>"
                    f'  <span class="source-badge">{SOURCE_LABELS[item["source"]]}</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with cols[1]:
                if st.button("Remove", key=f"remove_{i}", help="Delete topic", use_container_width=True):
                    del st.session_state.topic_list[i]
                    st.rerun()

    # Audio Generation Action
    section(
        "Audio Briefing",
        "Generate a natural audio broadcast from your configured topics.",
    )

    if st.button(
        "Generate Summary",
        type="primary",
        disabled=len(st.session_state.topic_list) == 0,
        use_container_width=True,
    ):
        topics_payload = [item["name"] for item in st.session_state.topic_list]
        trace_placeholder = st.empty()

        def update_trace(stage: str) -> None:
            with trace_placeholder.container():
                render_generation_trace(stage)

        update_trace("scraping")
        try:
            audio_bytes = generate_audio_briefing(
                topics_payload, on_progress=update_trace
            )
            if audio_bytes:
                with trace_placeholder.container():
                    render_generation_trace("audio")
                st.success("Audio news summary generated successfully!")
                st.audio(audio_bytes, format="audio/mpeg")
                st.download_button(
                    "Download MP3 Summary",
                    data=audio_bytes,
                    file_name="news-summary.mp3",
                    type="primary",
                    use_container_width=True,
                )

        except requests.exceptions.ConnectionError:
            st.error(
                f"Connection Error: Could not connect to backend at {BACKEND_URL}. Please ensure the FastAPI server is running."
            )
        except requests.exceptions.Timeout:
            st.error("The backend request timed out. Please try again.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()