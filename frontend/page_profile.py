"""
page_profile.py – Authenticated profile page.
"""

import streamlit as st
from frontend import api_client


def _require_auth() -> bool:
    if not st.session_state.token:
        st.warning("Please log in to view your profile.")
        if st.button("Go to login", key="profile_go_login"):
            st.session_state.page = "login"
            st.rerun()
        return False
    return True


def render() -> None:
    if not _require_auth():
        return

    st.markdown("## Profile")
    st.markdown("---")

    # Fetch fresh data
    resp = api_client.get_profile(st.session_state.token)
    if resp["status_code"] == 401:
        st.error("Session expired. Please log in again.")
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()
        return
    if resp["status_code"] != 200:
        st.error("Could not load profile.")
        return

    user = resp["data"]

    st.markdown(f"**Email:** {user['email']}")
    st.markdown(
        f"**Member since:** {user['created_at'][:10]}"  # YYYY-MM-DD
    )
    st.markdown("---")

    # Name update form
    st.markdown("### Update name")
    with st.form("profile_form"):
        new_name = st.text_input("Name", value=user["name"])
        submitted = st.form_submit_button("Save changes")

    if submitted:
        if not new_name.strip():
            st.error("Name must not be blank.")
            return
        update_resp = api_client.update_profile(st.session_state.token, new_name.strip())
        if update_resp["status_code"] == 200:
            st.session_state.user = update_resp["data"]
            st.success("Name updated successfully.")
        elif update_resp["status_code"] == 401:
            st.error("Session expired. Please log in again.")
            st.session_state.token = None
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Could not save changes.")

    st.markdown("---")
    if st.button("Logout", key="profile_logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.page = "home"
        st.rerun()
