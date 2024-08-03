import os
import streamlit as st
from game.arenas import Arena


def display_ranks():
    st.write("Rank table")
    column_config = {"LLM": st.column_config.TextColumn(width="small")}
    st.dataframe(data=Arena.rankings(), hide_index=True, column_config=column_config)


def display_sidebar():
    with st.sidebar:
        st.markdown("### LLM Rankings")
        if os.getenv("MONGO_URI"):
            if st.button("Calculate Ranks"):
                display_ranks()
        else:
            st.write(
                "LLM rankings aren't available as this app isn't connected to the database"
            )
