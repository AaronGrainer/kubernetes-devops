import streamlit as st

from common import config
from common.config import logger
from common.utils import send_request


def main():
    print("config: ", config)
    st.title(config.TITLE)
    st.write(config.DESCRIPTION)


if __name__ == "__main__":
    main()
