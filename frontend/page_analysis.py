"""
page_analysis.py – Text input and file upload sentiment analysis page.
"""

import csv
import io
import streamlit as st
from frontend import api_client


def _require_auth() -> bool:
    if not st.session_state.token:
        st.warning("Please log in to use the analysis tool.")
        if st.button("Go to login", key="analysis_go_login"):
            st.session_state.page = "login"
            st.rerun()
        return False
    return True


def _render_results(data: dict) -> None:
    """Display sentiment results and summary."""
    results = data.get("results", [])
    summary = data.get("summary", {})

    if len(results) > 1:
        st.markdown("### Summary")
        cols = st.columns(3)
        cols[0].metric("Positive", summary.get("Positive", 0))
        cols[1].metric("Negative", summary.get("Negative", 0))
        cols[2].metric("Neutral", summary.get("Neutral", 0))
        st.markdown("---")

    st.markdown("### Results")
    for i, r in enumerate(results, 1):
        prefix = f"**Row {i}**  " if len(results) > 1 else ""
        label = r["sentiment_label"]
        compound = r["compound_score"]

        # Simple label indicator without emojis
        label_display = f"[ {label} ]"

        with st.expander(f"{prefix}{label_display}  compound: {compound:+.4f}", expanded=(len(results) == 1)):
            st.markdown(f"**Original text:**")
            st.text(r["original_text"][:500] + ("…" if len(r["original_text"]) > 500 else ""))

            st.markdown(f"**Processed text:**")
            st.text(r["processed_text"][:500] if r["processed_text"] else "(empty after preprocessing)")

            st.markdown("**VADER scores:**")
            score_cols = st.columns(4)
            score_cols[0].metric("Compound", f"{r['compound_score']:+.4f}")
            score_cols[1].metric("Positive", f"{r['positive_score']:.4f}")
            score_cols[2].metric("Negative", f"{r['negative_score']:.4f}")
            score_cols[3].metric("Neutral", f"{r['neutral_score']:.4f}")


def render() -> None:
    if not _require_auth():
        return

    st.markdown("## Sentiment Analysis")
    st.markdown("Analyse the emotional tone of text using VADER.")
    st.markdown("---")

    tab_text, tab_file = st.tabs(["Text input", "File upload"])

    # ── Tab 1: text input ─────────────────────────────────────────────────────
    with tab_text:
        text_input = st.text_area(
            "Enter text to analyse",
            height=160,
            placeholder="Type or paste text here…",
            key="analysis_text",
        )
        if st.button("Analyse", key="btn_analyse_text"):
            if not text_input or not text_input.strip():
                st.error("Text must not be empty.")
            else:
                with st.spinner("Analysing…"):
                    try:
                        resp = api_client.analyze_text(st.session_state.token, text_input)
                    except Exception:
                        st.error("Could not reach the backend.")
                        return

                if resp["status_code"] == 200:
                    _render_results(resp["data"])
                elif resp["status_code"] == 401:
                    st.error("Session expired. Please log in again.")
                    st.session_state.token = None
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    detail = resp["data"].get("detail", "Analysis failed.")
                    st.error(detail)

    # ── Tab 2: file upload ────────────────────────────────────────────────────
    with tab_file:
        uploaded = st.file_uploader(
            "Upload a .txt or .csv file (max 2 MB)",
            type=["txt", "csv"],
            key="analysis_file",
        )

        csv_column = ""
        if uploaded and uploaded.name.lower().endswith(".csv"):
            # Peek at headers to allow column selection
            raw = uploaded.read()
            uploaded.seek(0)
            try:
                detected_text = raw.decode("utf-8", errors="replace")
                reader = csv.DictReader(io.StringIO(detected_text))
                headers = reader.fieldnames or []
                if headers:
                    csv_column = st.selectbox(
                        "Select the text column",
                        options=list(headers),
                        key="csv_col_select",
                    )
            except Exception:
                pass

        if st.button("Analyse file", key="btn_analyse_file"):
            if not uploaded:
                st.error("Please upload a file first.")
            else:
                uploaded.seek(0)
                file_bytes = uploaded.read()
                with st.spinner("Analysing…"):
                    try:
                        resp = api_client.analyze_file(
                            st.session_state.token,
                            file_bytes,
                            uploaded.name,
                            csv_column=csv_column,
                        )
                    except Exception:
                        st.error("Could not reach the backend.")
                        return

                if resp["status_code"] == 200:
                    _render_results(resp["data"])
                elif resp["status_code"] == 401:
                    st.error("Session expired. Please log in again.")
                    st.session_state.token = None
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    detail = resp["data"].get("detail", "Analysis failed.")
                    st.error(detail)
