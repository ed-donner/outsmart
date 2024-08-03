"""
Entry point for the Outsmart Arena LLM Battle
"""

import os

from dotenv import load_dotenv
import logging
from game.arenas import Arena
import streamlit as st
from util.setup import setup_logger, STYLE
from views.displays import Display

root = logging.getLogger()
if "root" not in st.session_state:
    st.session_state.root = root
    setup_logger(root)

load_dotenv()

st.set_page_config(
    layout="wide",
    page_title="Outsmart",
    menu_items={
        "About": "Outsmart is an LLM arena in which 4 LLMs compete by negotiating with each other. Read more at https://edwarddonner.com"
    },
    page_icon="🧠",
    initial_sidebar_state="collapsed",
)
st.markdown(STYLE, unsafe_allow_html=True)


if "arena" not in st.session_state:
    st.session_state.arena = Arena.default()

if "auto_move" not in st.session_state:
    st.session_state.auto_move = False
    st.session_state.do_move = False
arena = st.session_state.arena

Display(arena).display_page()
