from typing import Dict

import streamlit as st

from common import config
from common.utils import send_request as send_req


def send_auth_request(payload: Dict = {}):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    _, response = send_req(config.BACKEND_URL, "token", "POST", headers, payload)
    return response


def send_request(endpoint: str, method: str, payload: Dict = {}):
    access_token = st.session_state["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    status, response = send_req(config.BACKEND_URL, endpoint, method, headers, payload)
    if status == 401:
        st.session_state["authenticated"] = False

    return response
