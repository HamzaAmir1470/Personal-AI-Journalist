# Setup Streamlit
import html

import requests
import streamlit as st

BACKEND_URL = "http://localhost:1234"

# ---------------------------------------------------------------------------
# Styling (presentation only, no logic lives here)
# Colors are forced so the UI looks the same in Streamlit light or dark mode.
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
}

/* ---------- Base: white screen ---------- */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: #FFFFFF !important;
  color: var(--ink);
  color-scheme: light;
}
.stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label, .stApp input,
.stApp button, .stApp li, div[data-baseweb="popover"] {
  font-family: 'Bricolage Grotesque', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 880px; padding-top: 5.5rem; padding-bottom: 4rem; }

/* ---------- Header: white bar with the banner's gradient edge ---------- */
header[data-testid="stHeader"] {
  background: #FFFFFF !important;
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
[data-testid="stToolbar"] button:hover { background: #EEF0FF !important; border-radius: 10px; }

/* ---------- Hero ---------- */
.hero {
  position: relative; overflow: hidden; border-radius: 24px;
  padding: 34px 36px 30px;
  background: linear-gradient(120deg, #142036, #2B31B8, #3A3FD8, #142036);
  background-size: 300% 300%;
  animation: heroShift 14s ease infinite, riseIn .7s cubic-bezier(.2,.8,.2,1) both;
  box-shadow: 0 18px 40px -18px rgba(58,63,216,.55);
}
.hero h1 { margin: 0 0 6px; padding: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.05; color: #fff !important; }
.hero p { margin: 0; max-width: 46ch; font-size: 1.02rem; color: rgba(255,255,255,.85) !important; }
.flow { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.flow span { color: #fff !important; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.24); border-radius: 999px; padding: 4px 13px; font-size: .84rem; }
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
@keyframes pulseRing { 0% { box-shadow: 0 0 0 0 rgba(58,63,216,.45); } 100% { box-shadow: 0 0 0 14px rgba(58,63,216,0); } }

/* ---------- Section labels ---------- */
.section { display: flex; align-items: center; gap: 12px; margin: 30px 0 10px; font-weight: 600; font-size: 1.05rem; color: var(--ink); }
.section::after { content: ""; flex: 1; height: 1px; background: var(--line); }
.hint { color: var(--mute); font-size: .9rem; margin: -2px 0 10px; }

/* ---------- Text input ---------- */
.stTextInput label p { color: var(--ink) !important; font-weight: 600; }
.stTextInput div[data-baseweb="input"] {
  background: #FFFFFF !important; border: 1.5px solid var(--line) !important; border-radius: 14px !important;
  transition: border-color .2s, box-shadow .2s;
}
.stTextInput div[data-baseweb="input"]:focus-within { border-color: var(--acc) !important; box-shadow: 0 0 0 4px rgba(58,63,216,.14); }
.stTextInput div[data-baseweb="base-input"] { background: transparent !important; border: 0 !important; }
.stTextInput input {
  background: transparent !important; color: var(--ink) !important; -webkit-text-fill-color: var(--ink);
  padding: 12px 14px;
}
.stTextInput input::placeholder { color: #8A94A8 !important; -webkit-text-fill-color: #8A94A8; opacity: 1; }
[data-testid="InputInstructions"] { color: var(--mute) !important; }

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button {
  background: #FFFFFF; color: var(--ink); border: 1.5px solid var(--line); border-radius: 14px;
  font-weight: 600; padding: .6rem 1.1rem;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease, color .18s ease;
}
.stButton > button p, .stDownloadButton > button p { color: inherit !important; }
.stButton > button:hover:not(:disabled), .stDownloadButton > button:hover {
  transform: translateY(-2px); border-color: var(--acc); color: var(--acc);
  box-shadow: 0 10px 20px -12px rgba(58,63,216,.6);
}
.stButton > button:active:not(:disabled) { transform: translateY(0); }
.stButton > button:disabled { opacity: .45; cursor: not-allowed; }
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"], .stDownloadButton > button[data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, var(--acc), var(--acc-2)); color: #FFFFFF; border: 0;
}
.stButton > button[kind="primary"]:hover:not(:disabled), .stDownloadButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover:not(:disabled), .stDownloadButton > button[data-testid="stBaseButton-primary"]:hover {
  color: #FFFFFF; animation: pulseRing 1s ease-out infinite;
}

/* ---------- Topic chips ---------- */
.topic {
  display: flex; align-items: center; gap: 12px; background: #F6F8FD;
  border: 1px solid var(--line); border-radius: 14px; padding: 10px 14px;
  animation: popIn .35s cubic-bezier(.2,.8,.2,1) both; transition: border-color .2s, transform .2s;
}
.topic:hover { border-color: var(--acc); transform: translateX(3px); }
.topic .n { width: 26px; height: 26px; border-radius: 50%; display: grid; place-items: center; background: var(--acc); color: #fff; font-size: .82rem; font-weight: 600; }
.topic .t { font-weight: 600; color: var(--ink); }

/* ---------- Results ---------- */
.stAudio, .stDownloadButton { animation: riseIn .5s cubic-bezier(.2,.8,.2,1) both; }
.stAudio audio { width: 100%; }
.stSpinner p, [data-testid="stSpinner"] p { color: var(--ink) !important; }
[data-testid="stAlert"] { border-radius: 14px; background: #FDECEF; animation: riseIn .3s ease both; }
[data-testid="stAlert"] * { color: #8A1230 !important; }

/* ---------- Sidebar: black ---------- */
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div, [data-testid="stSidebarContent"] {
  background: var(--side) !important;
}
section[data-testid="stSidebar"] { border-right: 1px solid var(--side-line); }
section[data-testid="stSidebar"] * { color: #F4F6FF !important; }
section[data-testid="stSidebar"] h2 { font-weight: 800; letter-spacing: -0.02em; }
section[data-testid="stSidebar"] label p { font-weight: 600; color: #C9CEE6 !important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  background: var(--side-2) !important; border: 1.5px solid var(--side-line); border-radius: 14px; transition: border-color .2s;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover { border-color: var(--acc-2); }
section[data-testid="stSidebar"] div[data-baseweb="select"] svg { fill: #F4F6FF; }
div[data-baseweb="popover"] > div { background: var(--side-2) !important; border: 1px solid var(--side-line); border-radius: 14px; }
div[data-baseweb="popover"] ul { background: var(--side-2) !important; }
div[data-baseweb="popover"] li { background: transparent !important; color: #F4F6FF !important; }
div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] li[aria-selected="true"] { background: #252B5A !important; }

@media (max-width: 640px) {
  .hero { padding: 26px 22px; }
  .hero h1 { font-size: 1.9rem; }
  .wave { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
</style>
"""

HERO_HTML = (
    '<div class="hero">'
    '<div class="wave"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>'
    "<h1>Personal AI Journalist</h1>"
    "<p>Pick your topics and listen to a short audio news briefing built from your chosen sources.</p>"
    '<div class="flow"><span>Reddit</span><span>Google News</span><span>Summary</span><span>Audio</span></div>'
    "</div>"
)


def section(title, hint=None):
    """Render a styled section heading."""
    st.markdown(f'<div class="section">{title}</div>', unsafe_allow_html=True)
    if hint:
        st.markdown(f'<div class="hint">{hint}</div>', unsafe_allow_html=True)


def handle_api_error(response):
    """Handle API error responses."""
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

    # Initialize session state
    if "topics" not in st.session_state:
        st.session_state.topics = []

    # Setup sidebar
    with st.sidebar:
        st.header("Settings")
        source_type = st.selectbox(
            "Data Sources",
            options=["both", "news", "reddit"],
            format_func=lambda x: {
                "both": "Reddit + Google News",
                "news": "Google News",
                "reddit": "Reddit",
            }[x],
        )

    # Topic management
    section("Topic Management", "Add up to 3 topics you want to hear about.")
    col1, col2 = st.columns([4, 2])
    with col1:
        new_topic = st.text_input(
            "Enter a topic to analyze", placeholder="e.g. Artificial Intelligence"
        )
    with col2:
        # Spacer so the button lines up with the input box
        st.markdown('<div style="height:1.75rem"></div>', unsafe_allow_html=True)
        add_disabled = len(st.session_state.topics) >= 3 or not new_topic.strip()
        if st.button("Add topic", disabled=add_disabled, use_container_width=True):
            st.session_state.topics.append(new_topic.strip())
            st.rerun()

    if st.session_state.topics:
        section("Selected Topics")
        for i, topic in enumerate(st.session_state.topics[:3]):
            cols = st.columns([5, 1])
            cols[0].markdown(
                f'<div class="topic"><span class="n">{i+1}</span>'
                f'<span class="t">{html.escape(topic)}</span></div>',
                unsafe_allow_html=True,
            )
            if cols[1].button("Remove", key=f"remove_{i}", help="Delete topic"):
                del st.session_state.topics[i]
                st.rerun()

    # Analysis controls
    section("Audio Generation", "Your briefing is built from the topics and sources above.")

    if st.button(
        "Generate Summary",
        type="primary",
        disabled=len(st.session_state.topics) == 0,
    ):
        if not st.session_state.topics:
            st.error("Please add at least one topic")

        else:
            with st.spinner("Analyzing topics and generating audio ..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/generate-news-audio",
                        json={
                            "topics": st.session_state.topics,
                            "source_type": source_type,
                        },
                    )
                    if response.status_code == 200:
                        st.audio(response.content, format="audio/mpeg")
                        st.download_button(
                            "Download Audio Summary",
                            data=response.content,
                            file_name="news-summary.mp3",
                            type="primary",
                        )
                    else:
                        handle_api_error(response)

                except requests.exceptions.ConnectionError as e:
                    st.error(
                        f"Connection Error: Could not connect to backend at {BACKEND_URL}. Please ensure the backend server is running."
                    )
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
# User is able to write topics and mention sources of interest
# Show response from backend