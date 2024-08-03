import os
import logging
from typing import List, Self
from game.players import Player
from game.referees import Referee
import random
import pandas as pd
import math
from scipy.stats import rankdata
from models.games import Result, Game
from datetime import datetime
from trueskill import Rating


class Arena:
    """
    The manager of multiple Players competing in Outsmart
    """

    players: List[Player]
    turn: int
    is_game_over: bool

    def __init__(self, players: List[Player]):
        """
        Create a new instance of the Arena, the manager of the game
        Set the 'other players' field for each player. Shuffle it to reduce any bias on the order in which players
        are listed.
        :param players: the players to use
        """
        self.players = players
        for player in self.players:
            others = [p.name for p in players if p.name != player.name]
            random.shuffle(others)
            player.other_names = others
        self.turn = 1
        self.is_game_over = False

    def __repr__(self) -> str:
        """
        :return: a string to represent the receiver
        """
        result = f"Arena at turn {self.turn} with {len(self.players)} players:\n"
        for player in self.players:
            result += f"{player}\n"
        return result

    def do_save_game(
        self, names: List[str], llms: List[str], coins: List[int], ranks: List[int]
    ):
        results = []
        for name, llm, coin, rank in zip(names, llms, coins, ranks):
            r = Result(name=name, llm=llm, coins=coin, rank=rank)
            results.append(r)
        game = Game(run_date=datetime.now(), results=results)
        game.save()

    def save_game(self):
        if os.getenv("MONGO_URI"):
            try:
                names = [player.name for player in self.players]
                llms = [player.llm.model_name for player in self.players]
                coins = [player.coins for player in self.players]
                ranks = rankdata([-coin for coin in coins], method="min") - 1
                ranks = list(ranks.astype(int))
                self.do_save_game(names, llms, coins, ranks)
            except Exception as e:
                logging.error("Failed to save game results")
                logging.error(e)

    def handle_game_over(self):
        """The game has ended - figure out who's a winner; there could be multiple"""
        self.is_game_over = True
        winning_coins = max(player.coins for player in self.players)
        for player in self.players:
            if player.coins == winning_coins:
                player.is_winner = True
        self.save_game()

    def post_turn_solvency_check(self):
        """
        After a turn has completed, see if any player has run out of money. If so, end the game.
        """
        for player in self.players:
            if player.coins <= 0:
                player.coins = 0
                player.kill()
                self.handle_game_over()

    def do_turn(self, progress) -> bool:
        """
        Carry out a Turn; delegate to a Referee to manage this process
        :param progress: an object on which to report progress that will be reflected in the UI
        :return True if the game ended
        """
        for player in self.players:
            player.prior_coins = player.coins
        ref = Referee(self.players, self.turn)
        ref.do_turn(progress)
        for player in self.players:
            player.series.append(player.coins)
        self.post_turn_solvency_check()
        if self.turn == 10:
            self.handle_game_over()
        elif not self.is_game_over:
            self.turn += 1
        return self.is_game_over

    @classmethod
    def default(cls) -> Self:
        """
        Return a new instance of Arena with default players
        :return: an Arena instance
        """
        names = ["Alex", "Blake", "Charlie", "Drew"]
        model_names = [
            "gpt-3.5-turbo",
            "claude-3-haiku-20240307",
            "gemini-pro",
            "gpt-4o-mini",
        ]
        temperatures = [0.7, 0.7, 0.7, 0.7]
        players = []
        for data in zip(names, model_names, temperatures):
            players.append(Player(data[0], data[1], data[2]))
        return cls(players)

    def turn_name(self) -> str:
        return f"Turn {self.turn}"

    def table(self) -> pd.DataFrame:
        d = {}
        padding = [math.nan] * (11 - self.turn)
        for player in self.players:
            series = player.series[:] + padding
            d[player.name] = series[:11]
        return pd.DataFrame(data=d, index=range(11))

    @staticmethod
    def rankings() -> pd.DataFrame:
        df = Game.games_df()
        df = df.sort_values(by="Skill", ascending=False)
        return df
