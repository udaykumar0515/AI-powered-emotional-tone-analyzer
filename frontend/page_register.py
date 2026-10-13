"""
page_register.py – Registration page.
"""

import re
import streamlit as st
from frontend import api_client

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def render() -> None:
    if st.session_state.token:
        st.session_state.page = "analysis"
        st.rerun()

    st.markdown("## Create an account")
    st.markdown("Fill in the details below to register.")
    st.markdown("---")

    with st.form("register_form"):
        name = st.text_input("Name", placeholder="Your full name")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", help="At least 6 characters")
        submitted = st.form_submit_button("Register")

    if submitted:
        # Client-side validation
        errors = []
        if not name.strip():
            errors.append("Name is required.")
        if not email.strip():
            errors.append("Email is required.")
        elif not _EMAIL_RE.match(email.strip()):
            errors.append("Enter a valid email address.")
        if not password:
            errors.append("Password is required.")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters.")

        if errors:
            for e in errors:
                st.error(e)
            return

        try:
            resp = api_client.register(name.strip(), email.strip(), password)
        except Exception:
            st.error("Could not reach the backend. Is the server running?")
            return

        if resp["status_code"] == 201:
            st.success("Account created. You can now log in.")
            st.session_state.page = "login"
            st.rerun()
        elif resp["status_code"] == 409:
            st.error("An account with this email already exists.")
        elif resp["status_code"] == 422:
            detail = resp["data"].get("detail", "Validation error.")
            st.error(f"Validation error: {detail}")
        else:
            st.error("Registration failed. Please try again.")

    st.markdown("---")
    st.markdown("Already have an account?")
    if st.button("Login", key="register_to_login"):
        st.session_state.page = "login"
        st.rerun()
