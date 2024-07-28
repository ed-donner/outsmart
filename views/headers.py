import streamlit as st
import base64
from io import BytesIO


def display_overview(arena, callback):
    st.markdown("<h1 style='text-align: center;'>Outsmart</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center;'>A battle of diplomacy and deviousness between LLMs</p>",
        unsafe_allow_html=True,
    )
    button_columns = st.columns([0.2, 1, 0.2, 1, 0.2])
    with button_columns[1]:
        st.button(
            f"Run Turn {arena.turn}",
            disabled=arena.is_game_over,
            on_click=callback,
            use_container_width=True,
        )
    with button_columns[3]:
        st.button("Run Game", use_container_width=True)


def display_image():
    with open("outsmart_image_base64.txt", "r") as f:
        base64_string = f.read()
    image_data = base64.b64decode(base64_string)
    st.image(BytesIO(image_data), use_column_width="auto")


def display_details():
    st.write(
        """###### Each turn, players:
- Take 1 coin & give 1 coin to another
- Exchange private messages to negotiate
- Try to form alliances to win extra coins"""
    )
    st.write(
        """Read about the [game](https://edwarddonner.com)  
Clone the [repo](https://github.com/ed-donner/outsmart) to battle frontier models"""
    )


def display_headers(arena, callback):
    header_columns = st.columns([1.5, 0.5, 2, 0.2, 1.8])
    with header_columns[0]:
        display_image()
    with header_columns[2]:
        display_overview(arena, callback)
    with header_columns[4]:
        display_details()
