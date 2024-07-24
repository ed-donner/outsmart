from typing import Optional, List, Dict, Self
from models.moves import Move


class TurnRecord:
    """
    This tracks the key information associated with a turn for a particular player
    """

    turn: int
    name: str
    is_invalid_move: bool
    move: Optional[Move] = None
    givers: List[str]
    takers: List[str]
    alliances_with: List[str]
    alliances_against: List[str]
    messages: Dict[str, str]

    def __init__(self, name: str, turn: int, move=None, is_invalid_move=False):
        """
        Initialize a new instance
        :param name: The name of the player
        :param turn: Which turn it is
        :param is_invalid_move: if the response JSON was badly formed or made an illegal move
        """
        self.name = name
        self.turn = turn
        self.is_invalid_move = is_invalid_move
        self.givers = []
        self.takers = []
        self.alliances_with = []
        self.alliances_against = []
        self.messages = {}
        self.move = move

    def __repr__(self) -> str:
        """
        :return: a string to represent this instance
        """
        result = f"Recap of Turn {self.turn}\n\n"
        result += "Your actions:\n"
        if self.is_invalid_move:
            result += "You provided invalid JSON, so your move was not processed"
        else:
            result += f"Your secret strategy: {self.move.strategy}\n"
            result += f"You gave a coin to {self.move.give}\n"
            result += f"You took a coin from {self.move.take}\n"
            result += "You sent these private messages:\n"
            for recipient, message in self.move.messages.items():
                result += f"Message to {recipient}: {message}\n"
        result += "\nResults of the turn:\n"

        givers = ", ".join(self.givers)
        takers = ", ".join(self.takers)
        alliances_with = ", ".join(self.alliances_with)
        alliances_against = ", ".join(self.alliances_against)

        if self.givers:
            result += f"These players gave you a coin: {givers}\n"
        else:
            result += "No players gave you coins\n"

        if self.takers:
            result += f"These players took a coin from you: {takers}\n"
        else:
            result += "No players took coins from you\n"

        if self.alliances_with:
            result += f"These players formed an alliance with you: {alliances_with}\n"

        if self.alliances_against:
            result += (
                f"These players formed an alliance against you: {alliances_against}\n"
            )

        result += "You received these private messages:\n"
        for sender, message in self.messages.items():
            result += f"Message from {sender}: {message}\n"
        result += "\n"
        return result
