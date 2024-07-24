import logging
from game.arenas import Arena
import streamlit as st


class Display:

    arena: Arena

    def __init__(self, arena: Arena):
        self.arena = arena

    def display_record(self, rec):
        if rec.is_invalid_move:
            st.write("Illegal last move")
        else:
            st.write(f"Strategy: {rec.move.strategy}")
            st.write(f"Gave to {rec.move.give}")
            st.write(f"Took from {rec.move.take}")
        if len(rec.alliances_with) > 0:
            alliances = ", ".join(rec.alliances_with)
            st.write(f"In an alliance with {alliances}")
        if len(rec.alliances_against) > 0:
            alliances = ", ".join(rec.alliances_against)
            st.write(f"Being ganged up on by {alliances}")

    def display_player_title(self, each):
        if each.is_dead:
            st.header(f":red[{each.name}]")
        elif each.is_winner:
            st.header(f":green[{each.name}]")
        else:
            st.header(f":blue[{each.name}]")

    def display_player(self, each):
        self.display_player_title(each)
        st.write(each.llm.model_name)
        records = each.records
        st.metric("Coins", each.coins, each.coins - each.prior_coins)
        with st.expander("Inner thoughts", expanded=False):
            st.markdown(
                f'<p class="small-font">{each.report()}</p>', unsafe_allow_html=True
            )
        if len(records) > 0:
            record = records[-1]
            self.display_record(record)

    def do_turn(self):
        logging.info("Kicking off turn")
        progress_text = "Kicking off turn"
        bar = st.progress(0.0, text=progress_text)
        self.arena.do_turn(bar)
        bar.empty()

    def display_page(self):
        st.title("Outsmart")
        st.write("A battle of diplomacy and deviousness between LLMs")
        st.button(f"Run Turn {self.arena.turn}", disabled=self.arena.is_game_over, on_click=self.do_turn)
        player_columns = st.columns(len(self.arena.players))

        for index, player_column in enumerate(player_columns):
            player = self.arena.players[index]
            with player_column:
                self.display_player(player)
