"""
app.py – MoodMentor Streamlit application entry point.

Navigation
----------
Landing  – public home page
Login    – credential form
Register – registration form
Analysis – text / file sentiment analysis (authenticated)
Profile  – view and update name (authenticated)
"""

import streamlit as st

st.set_page_config(
    page_title="MoodMentor",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Enhanced styling & theme compatibility ────────────────────────────────────
st.markdown(
    """
<style>
/* Fix header clipping bug: give sufficient space below Streamlit's top header bar */
header[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 1 !important;
}

.block-container {
    padding-top: 5rem !important;
    padding-bottom: 3rem !important;
    max-width: 820px !important;
}

/* Nav brand */
.nav-brand {
    font-size: 1.35rem;
    font-weight: 700;
    padding-top: 4px;
    letter-spacing: -0.02em;
}

/* Input fields & text visibility (dark theme & autofill support) */
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background-color: #1e222d !important;
    border: 1px solid #3b4252 !important;
    border-radius: 6px !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input,
.stTextInput input,
.stTextArea textarea,
input, textarea {
    color: #f3f4f6 !important;
    -webkit-text-fill-color: #f3f4f6 !important;
    background-color: #1e222d !important;
    caret-color: #60a5fa !important;
    font-size: 0.95rem !important;
}

/* Browser autofill styling so text remains clearly visible */
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 40px #1e222d inset !important;
    -webkit-text-fill-color: #f3f4f6 !important;
    caret-color: #60a5fa !important;
}

/* Placeholder styling */
input::placeholder, textarea::placeholder {
    color: #9ca3af !important;
    -webkit-text-fill-color: #9ca3af !important;
    opacity: 1 !important;
}

/* Buttons */
.stButton > button {
    border-radius: 6px;
    padding: 0.45rem 1.25rem;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.15s ease-in-out;
}

/* Dividers */
hr {
    border: none;
    border-top: 1px solid rgba(128, 128, 128, 0.25);
    margin: 1.25rem 0;
}

/* Sentiment result box */
.result-box {
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Session defaults ──────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"


def go(page: str) -> None:
    st.session_state.page = page
    st.rerun()


# ── Navigation bar ────────────────────────────────────────────────────────────
def nav_bar() -> None:
    if st.session_state.token:
        cols = st.columns([3, 1, 1, 1])
        with cols[0]:
            st.markdown(
                "<div class='nav-brand'>MoodMentor</div>",
                unsafe_allow_html=True,
            )
        if cols[1].button("Analysis", key="nav_analysis", use_container_width=True):
            go("analysis")
        if cols[2].button("Profile", key="nav_profile", use_container_width=True):
            go("profile")
        if cols[3].button("Logout", key="nav_logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            go("home")
    else:
        cols = st.columns([4, 1, 1])
        with cols[0]:
            st.markdown(
                "<div class='nav-brand'>MoodMentor</div>",
                unsafe_allow_html=True,
            )
        if cols[1].button("Login", key="nav_login", use_container_width=True):
            go("login")
        if cols[2].button("Register", key="nav_register", use_container_width=True):
            go("register")
    st.markdown("---")


# ── Pages ─────────────────────────────────────────────────────────────────────
from frontend import page_home, page_login, page_register, page_analysis, page_profile  # noqa: E402

page_map = {
    "home": page_home.render,
    "login": page_login.render,
    "register": page_register.render,
    "analysis": page_analysis.render,
    "profile": page_profile.render,
}

nav_bar()
render_fn = page_map.get(st.session_state.page, page_home.render)
render_fn()
