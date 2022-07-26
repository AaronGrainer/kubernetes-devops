import streamlit as st

from common import config
from frontend.utils import send_auth_request


def check_password():
    """Returns `True` if the user had a correct password."""

    # Auto-authentication for development use
    if config.AUTO_AUTH:
        if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
            payload = {"username": config.BACKEND_USERNAME, "password": config.BACKEND_PASSWORD}
            response = send_auth_request(payload)
            st.session_state["access_token"] = response["access_token"]
            st.session_state["authenticated"] = True

    # Normal authentication
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        username = st.session_state["username"]
        password = st.session_state["password"]

        payload = {"username": username, "password": password}
        response = send_auth_request(payload)
        if response:
            st.session_state["access_token"] = response["access_token"]
            st.session_state["authenticated"] = True

            # Clear username and password from session_state
            del st.session_state["username"]
            del st.session_state["password"]
        else:
            st.session_state["authenticated"] = False

    if "authenticated" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["authenticated"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True
