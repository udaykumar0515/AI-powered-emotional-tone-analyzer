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

# ── Minimal global CSS ────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* Typography and background */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background-color: #f9f9f7;
    color: #2c2c2c;
}

/* Remove default Streamlit top padding */
.block-container { padding-top: 2rem; }

/* Headings */
h1 { font-size: 1.9rem; font-weight: 700; color: #1a1a1a; margin-bottom: 0.25rem; }
h2 { font-size: 1.3rem; font-weight: 600; color: #2c2c2c; }
h3 { font-size: 1.05rem; font-weight: 600; color: #2c2c2c; }

/* Input fields */
input, textarea {
    border: 1px solid #d0d0d0 !important;
    border-radius: 4px !important;
    background: #ffffff !important;
}

/* Buttons */
.stButton > button {
    background-color: #2c2c2c;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 0.45rem 1.4rem;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
}
.stButton > button:hover {
    background-color: #444444;
}

/* Dividers */
hr { border: none; border-top: 1px solid #e0e0e0; margin: 1.5rem 0; }

/* Sentiment result table */
.result-box {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

/* Navigation pills */
.nav-bar { display: flex; gap: 0.75rem; margin-bottom: 1.5rem; }
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
    cols = st.columns([2, 1, 1, 1, 1])
    cols[0].markdown("**MoodMentor**")
    if st.session_state.token:
        if cols[2].button("Analysis", key="nav_analysis"):
            go("analysis")
        if cols[3].button("Profile", key="nav_profile"):
            go("profile")
        if cols[4].button("Logout", key="nav_logout"):
            st.session_state.token = None
            st.session_state.user = None
            go("home")
    else:
        if cols[3].button("Login", key="nav_login"):
            go("login")
        if cols[4].button("Register", key="nav_register"):
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
