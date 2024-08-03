import os
import streamlit as st
from game.arenas import Arena
from models.games import Game


def display_ranks():
    st.write("Rank table")
    st.write(
        "The skill level of each LLM using the TrueSkill methodology,"
        " ELO-style ratings for multi-player games."
    )
    column_config = {
        "LLM": st.column_config.TextColumn(width="small"),
        "Win %": st.column_config.NumberColumn(format="%.1f"),
        "Skill": st.column_config.NumberColumn(format="%.1f"),
    }
    st.dataframe(data=Arena.rankings(), hide_index=True, column_config=column_config)


def display_latest():
    st.write("Latest games")
    column_config = {
        "When": st.column_config.DatetimeColumn(width="small"),
        "Winner(s)": st.column_config.TextColumn(width="medium"),
    }
    st.dataframe(data=Arena.latest(), hide_index=True, column_config=column_config)


def display_coffee():
    st.write(
        "If you enjoyed this app, I'm super grateful for any recognition, but not required at all!"
    )
    st.markdown(
        """
        <div style="display: flex; justify-content: left;">
            <a href="https://www.buymeacoffee.com/ed.donner" target="_blank">
                <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px; width: 150px;">
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_sidebar():
    with st.sidebar:
        st.markdown("### LLM Rankings")
        if os.getenv("MONGO_URI"):
            try:
                st.write(f"There have been {Game.count():,} games recorded.")
                if st.button("Calculate Rankings"):
                    display_ranks()
                    display_latest()
            except Exception as e:
                st.write(
                    "Unable to calculate rankings - the database may not be available."
                )
                st.write(f"Underlying error was {e}")
        else:
            st.write(
                "LLM rankings aren't available as this app isn't connected to the database"
            )
        display_coffee()
