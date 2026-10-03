import html
import requests
import streamlit as st

BACKEND_URL = "http://localhost:1234"

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
  background-color: #FFFFFF !important;
  border-bottom: 1px solid var(--line);
  height: 3.5rem;
}

header[data-testid="stHeader"]::after {
  content: "";
  position: absolute; left: 0; right: 0; bottom: -1px; height: 3px;
  background: linear-gradient(90deg, #142036, #2B31B8, #3A3FD8, #6C70FF, #FFD166, #3A3FD8, #142036);
  background-size: 300% 100%;
  animation: edgeShift 10s linear infinite;
}

header[data-testid="stHeader"] *, [data-testid="stToolbar"] * { color: var(--ink) !important; }

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

/* ---------- Dark Sidebar ---------- */
section[data-testid="stSidebar"] {
  background-color: var(--side) !important;
  border-right: 1px solid var(--side-line);
}
section[data-testid="stSidebar"] * { color: var(--side-ink) !important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  background-color: var(--side-2) !important; border: 1.5px solid var(--side-line) !important; border-radius: 14px;
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

        with st.spinner("Scraping news sources and synthesizing audio..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate-news-audio",
                    json={
                        "topics": topics_payload,
                        "source_type": source_type,
                    },
                )
                if response.status_code == 200:
                    st.success("Audio news summary generated successfully!")
                    st.audio(response.content, format="audio/mpeg")
                    st.download_button(
                        "Download MP3 Summary",
                        data=response.content,
                        file_name="news-summary.mp3",
                        type="primary",
                        use_container_width=True,
                    )
                else:
                    handle_api_error(response)

            except requests.exceptions.ConnectionError:
                st.error(
                    f"Connection Error: Could not connect to backend at {BACKEND_URL}. Please ensure the FastAPI server is running."
                )
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()