import streamlit as st
import base64
from io import BytesIO
from game.arenas import Arena
from typing import Callable


def display_overview(arena: Arena, do_turn: Callable, do_auto_turn: Callable) -> None:
    """
    Show the top middle sections of the header, including the buttons andlinks
    :param arena: the arena being run
    :param do_turn: callback to run a turn
    :param do_auto_turn: callback to run the game
    """
    st.markdown("<h1 style='text-align: center;'>Outsmart</h1>", unsafe_allow_html=True)
    st.markdown(
        """<p style='text-align: center;'>A battle of diplomacy and deviousness between LLMs<br/>
        Read the <a href='https://edwarddonner.com/2024/08/06/outsmart/'>backstory</a>
        or clone the <a href='https://github.com/ed-donner/outsmart'>repo</a> to battle frontier models<br/>
        <span style='text-align: center; font-size:13px;'>Open the sidebar for the leaderboard</span>
        </p>""",
        unsafe_allow_html=True,
    )

    button_columns = st.columns([1, 0.1, 1, 0.1, 1])
    with button_columns[0]:
        st.button(
            f"Run Turn {arena.turn}",
            disabled=arena.is_game_over,
            on_click=do_turn,
            use_container_width=True,
        )
    with button_columns[2]:
        st.button(
            "Run Game",
            disabled=arena.is_game_over,
            on_click=do_auto_turn,
            use_container_width=True,
        )
    with button_columns[4]:
        if st.button(
            "Restart Game",
            use_container_width=True,
        ):
            del st.session_state.arena
            st.rerun()


def display_image() -> None:
    """
    Show the image of the game. This needed to be base64 encoded due to Hugging Face not allowing
    binary files in repos
    """
    with open("outsmart_image_base64.txt", "r") as f:
        base64_string = f.read()
    image_data = base64.b64decode(base64_string)
    st.image(BytesIO(image_data), use_column_width="auto")


def display_details(header_container: st.container) -> None:
    """
    Show the game rules at the start of the game
    :param header_container: where to put the rules; needed so we can replace it with a chart
    """
    with header_container:
        st.write("  \n")
        st.write(
            """###### Each turn, players:
- Take 1 coin & give 1 coin to another
- Exchange private messages to negotiate
- Try to form alliances to win extra coins"""
        )


def display_chart(arena: Arena, header_container: st.container):
    """
    Show the line chart of coin progress
    :param arena: the underlying arena
    :param header_container: where to put the chart; needed so it replaces the instructions
    """
    with header_container:
        st.line_chart(
            data=arena.table(),
            height=300,
            color=["#FFA500", "#FF4500", "#FFD700", "#8B4513"],
        )


def display_headers(arena: Arena, do_turn: Callable, do_auto_turn: Callable) -> None:
    """
    Display the top 3 sections of the page
    :param arena: the underlying arena
    :param do_turn: a callboack to run the next turn
    :param do_auto_turn: a callback to trigger running of the entire game
    """
    header_columns = st.columns([1.5, 0.5, 2, 0.2, 1.8])
    with header_columns[0]:
        display_image()
    with header_columns[2]:
        display_overview(arena, do_turn, do_auto_turn)
    with header_columns[4]:
        header_container = st.empty()
        if arena.turn == 1:
            display_details(header_container)
        else:
            display_chart(arena, header_container)
