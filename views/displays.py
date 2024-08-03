import logging
from game.arenas import Arena
import streamlit as st
from views.headers import display_headers
from views.sidebars import display_sidebar
from streamlit_extras.buy_me_a_coffee import button as coffee
import streamlit.components.v1 as components


class Display:

    arena: Arena

    def __init__(self, arena: Arena):
        self.arena = arena
        self.progress_container = None

    def display_record(self, rec):
        if rec.is_invalid_move:
            text = "Illegal last move"
        else:
            text = f"Strategy: {rec.move.strategy}  \n\n"
            text += f"- Gave to {rec.move.give}\n"
            text += f"- Took from {rec.move.take}\n"
        if len(rec.alliances_with) > 0:
            alliances = ", ".join(rec.alliances_with)
            text += f"- :green[In an alliance with {alliances}]\n"
        if len(rec.alliances_against) > 0:
            alliances = ", ".join(rec.alliances_against)
            text += f"- :red[Being ganged up on by {alliances}]"
        st.write(text)

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
        with self.progress_container.container():
            bar = st.progress(0.0, text=progress_text)
        self.arena.do_turn(bar)
        bar.empty()

    def do_auto_turn(self):
        st.session_state.auto_move = False
        self.do_turn()
        if not self.arena.is_game_over:
            st.session_state.auto_move = True

    def display_page(self):
        display_sidebar()
        display_headers(self.arena, self.do_turn, self.do_auto_turn)
        self.progress_container = st.empty()
        player_columns = st.columns(len(self.arena.players))

        for index, player_column in enumerate(player_columns):
            player = self.arena.players[index]
            with player_column:
                inner = st.empty()
                with inner.container():
                    self.display_player(player)

        # coffee(username="ed.donner", floating=True, width=221)

        if st.session_state.auto_move:
            self.do_auto_turn()
            st.rerun()
