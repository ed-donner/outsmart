import os
import streamlit as st
from game.arenas import Arena
from models.games import Game


def display_ranks():
    st.markdown(
        "<span style='font-size:13px;'>The table is sorted initially by Win %. "
        "The skill ratings use the TrueSkill methodology,"
        " an ELO-style system for multi-player games.</span>",
        unsafe_allow_html=True,
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
    st.markdown(
        "<span style='font-size:13px;'>If you enjoyed Outsmart, I'm super grateful for any recognition, but not required at all!</span>",
        unsafe_allow_html=True,
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
        st.markdown("### Outsmart Leaderboard")
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
