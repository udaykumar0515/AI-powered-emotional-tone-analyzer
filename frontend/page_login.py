"""
page_login.py – Login page.
"""

import streamlit as st
from frontend import api_client


def render() -> None:
    if st.session_state.token:
        st.session_state.page = "analysis"
        st.rerun()

    st.markdown("## Login")
    st.markdown("Enter your registered email and password.")
    st.markdown("---")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if not email.strip() or not password:
            st.error("Please fill in both fields.")
            return

        try:
            resp = api_client.login(email.strip(), password)
        except Exception:
            st.error("Could not reach the backend. Is the server running?")
            return

        if resp["status_code"] == 200:
            token = resp["data"]["access_token"]
            st.session_state.token = token

            # Fetch user info
            me = api_client.get_me(token)
            if me["status_code"] == 200:
                st.session_state.user = me["data"]

            st.success("Logged in successfully.")
            st.session_state.page = "analysis"
            st.rerun()
        elif resp["status_code"] == 401:
            st.error("Incorrect email or password.")
        else:
            st.error("Login failed. Please try again.")

    st.markdown("---")
    st.markdown("Don't have an account?")
    if st.button("Register", key="login_to_register"):
        st.session_state.page = "register"
        st.rerun()
