import os
import logging
from typing import List, Self, Callable
from game.players import Player
from game.referees import Referee
import random
import pandas as pd
import math
from scipy.stats import rankdata
from models.games import Result, Game
from datetime import datetime
from interfaces.llms import LLM

ProgressCallback = Callable[[float, str], None]


class Arena:
    """
    The central Game Manager for the Outsmart LLM arena, managing a list of players
    """

    players: List[Player]
    turn: int
    is_game_over: bool

    NAMES = ["Alex", "Blake", "Charlie", "Drew", "Eden", "Fallon", "Gale", "Harper"]
    TEMPERATURE = 0.7

    def __init__(self, players: List[Player]):
        """
        Create a new instance of the Arena, the manager of the game
        Set the 'other players' field for each player. Shuffle it to reduce any bias on the order in which players
        are listed.
        :param players: the players to use
        """
        self.players = players
        for player in self.players:
            others = [p for p in players if p.name != player.name]
            random.shuffle(others)
            player.others = others
        self.turn = 1
        self.is_game_over = False

    def __repr__(self) -> str:
        """
        :return: a string to represent the arena
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
        game_ended = False
        for player in self.players:
            if player.coins <= 0:
                player.coins = 0
                player.kill()
                game_ended = True
        if game_ended:
            self.handle_game_over()

    def prepare_for_turn(self) -> None:
        """
        Before carrying out a turn, store the coins each player had initially
        """
        for player in self.players:
            player.prior_coins = player.coins

    def process_turn_outcome(self) -> None:
        """
        A turn has completed. Handle the outcome, including checking if the game has ended
        """
        for player in self.players:
            player.series.append(player.coins)
        self.post_turn_solvency_check()
        if self.turn == 10:
            self.handle_game_over()
        elif not self.is_game_over:
            self.turn += 1

    def do_turn(self, progress: ProgressCallback) -> bool:
        """
        Carry out a Turn by delegating to a Referee object
        :param progress: a callback on which to report progress
        :return True if the game ended
        """
        self.prepare_for_turn()
        ref = Referee(self.players, self.turn)
        ref.do_turn(progress)
        self.process_turn_outcome()
        return self.is_game_over

    @classmethod
    def model_names(cls) -> List[str]:
        """
        Determine the list of model names to use in a new Arena
        If there's an environment variable ARENA=random then pick 4 random model names
        otherwise use 4 cheap models
        The arena should support 3 or more names, although only 4 has been tested
        :return: a list of names of LLMs for a new Arena
        """
        arena_type = os.getenv("ARENA")
        if arena_type == "random":
            return random.sample(LLM.all_model_names(), 4)
        else:
            return [
                "gpt-3.5-turbo",
                "claude-3-haiku-20240307",
                "gemini-1.0-pro",
                "gpt-4o-mini",
            ]

    @classmethod
    def default(cls) -> Self:
        """
        Return a new instance of Arena with default players
        :return: an Arena instance
        """
        names = cls.NAMES
        model_names = cls.model_names()
        players = [
            Player(name, model_name, cls.TEMPERATURE)
            for name, model_name in zip(names, model_names)
        ]
        return cls(players)

    def turn_name(self) -> str:
        return f"Turn {self.turn}"

    def table(self) -> pd.DataFrame:
        """
        Create the table of coins by turn that will be used to make a line chart of each player
        Use NaN to fill up each row to 10 datapoints so that the axes display properly;
        The NaN values don't show on the line chart
        :return: a dataframe that shows how each players' coins have evolved during the game
        """
        d = {}
        padding = [math.nan] * (11 - self.turn)
        for player in self.players:
            series = player.series[:] + padding
            d[player.name] = series[:11]
        return pd.DataFrame(data=d, index=range(11))

    @staticmethod
    def rankings() -> pd.DataFrame:
        """
        Create the leaderboard, delegating to the Game business object to handle this
        :return: a dataframe with the leaderboard info
        """
        df = Game.games_df()
        df = df.sort_values(by="Win %", ascending=False)
        return df

    @staticmethod
    def latest() -> pd.DataFrame:
        """
        Create the table of last N games, delegating to the Game business object
        :return: a dataframe with the most recent results of games
        """
        return Game.latest_df()
