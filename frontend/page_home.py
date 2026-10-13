"""
page_home.py – Landing page.
"""

import streamlit as st
from frontend import api_client


def render() -> None:
    # Backend status notice
    if not api_client.health():
        st.warning(
            "Backend is not reachable. Start the FastAPI server before using the application."
        )

    st.markdown("# MoodMentor")
    st.markdown(
        "An AI-powered tool that analyses the emotional tone of text and "
        "provides a structured sentiment report."
    )

    st.markdown("---")

    st.markdown("### What it does")
    st.markdown(
        """
MoodMentor applies **VADER sentiment analysis** to text you provide — either
typed directly or uploaded as a plain-text or CSV file.

For each input, it returns:

- A sentiment label — **Positive**, **Negative**, or **Neutral**
- A compound score between −1 (most negative) and +1 (most positive)
- A breakdown of positive, negative, and neutral component scores
- A cleaned, lemmatised representation of the text

The application is the first milestone of a larger emotional tone analysis
and well-being recommendation system.
"""
    )

    st.markdown("---")

    st.markdown("### Get started")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Register", key="home_register", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()
    with col2:
        if st.button("Login", key="home_login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
