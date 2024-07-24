from typing import List, Self
from game.players import Player
from game.referees import Referee
import random


class Arena:
    """
    The manager of multiple Players competing in Outsmart
    """

    players: List[Player]
    turn: int
    is_game_over: bool

    def __init__(self, players: List[Player]):
        """
        Create a new instance of the receiver
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

    def handle_game_over(self):
        """The game has ended - figure out who's a winner; there could be multiple"""
        self.is_game_over = True
        winning_coins = max(player.coins for player in self.players)
        for player in self.players:
            if player.coins == winning_coins:
                player.is_winner = True

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
