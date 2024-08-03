import streamlit as st
import base64
from io import BytesIO


def display_overview(arena, do_turn, do_auto_turn):
    st.markdown("<h1 style='text-align: center;'>Outsmart</h1>", unsafe_allow_html=True)
    st.markdown(
        """<p style='text-align: center;'>A battle of diplomacy and deviousness between LLMs<br/>
        <span style='text-align: center; font-size:13px;'>Read the <a href='https://edwarddonner.com'>backstory</a> or clone the <a href='https://github.com/ed-donner/outsmart'>repo</a> to battle frontier models</span><br/>
        <span style='text-align: center; font-size:13px;'>Open the sidebar for results and rankings</span>
        </p>""",
        unsafe_allow_html=True,
    )
    button_columns = st.columns([0.2, 1, 0.2, 1, 0.2])
    with button_columns[1]:
        st.button(
            f"Run Turn {arena.turn}",
            disabled=arena.is_game_over,
            on_click=do_turn,
            use_container_width=True,
        )
    with button_columns[3]:
        st.button(
            "Run Game",
            disabled=arena.is_game_over,
            use_container_width=True,
            on_click=do_auto_turn,
        )


def display_image():
    with open("outsmart_image_base64.txt", "r") as f:
        base64_string = f.read()
    image_data = base64.b64decode(base64_string)
    st.image(BytesIO(image_data), use_column_width="auto")


def display_details(header_container):
    with header_container:
        st.write("  \n")
        st.write(
            """###### Each turn, players:
- Take 1 coin & give 1 coin to another
- Exchange private messages to negotiate
- Try to form alliances to win extra coins"""
        )


def display_chart(arena, header_container):
    with header_container:
        st.line_chart(
            data=arena.table(),
            height=300,
            color=["#FFA500", "#FF4500", "#FFD700", "#8B4513"],
        )


def display_headers(arena, do_turn, do_auto_turn):
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
