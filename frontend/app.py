import streamlit as st

from common import config
from frontend.authentication import check_password
from frontend.utils import send_request


def main():
    st.title(config.TITLE)
    st.write(config.DESCRIPTION)


if __name__ == "__main__":
    if check_password():
        main()
