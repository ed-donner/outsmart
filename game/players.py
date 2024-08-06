from typing import List, Dict, Any, Self
from interfaces.llms import LLM
from prompting.system import instructions
from prompting.user import prompt
from models.records import TurnRecord


class Player:
    """
    A particular Player in the game of Outsmart
    The player has a name, and an underlying llm (an instance of a subclass of interface.llms.LLM)
    All LLM interactions are delegated to the LLM object.
    """

    name: str
    llm: LLM
    others: List[Self]
    history: Dict[str, Any]
    coins: int
    records: List[TurnRecord]
    is_dead: bool
    is_winner: bool
    series: List[int]

    MAX_TOKENS = 600

    def __init__(self, name: str, model_name: str, temperature: float):
        """
        Create a new instance of Player
        :param name: The Player's name, as the others will address them
        :param model_name: Which LLM model to use
        :param temperature: The temperature setting for the model, so that different temp models can compete
        """
        self.name = name
        self.llm = LLM.for_model_name(model_name, temperature)
        self.history = {}
        self.coins = 12
        self.prior_coins = 12
        self.series = [12]
        self.others = []  # this will be initialized during Arena construction
        self.records = []
        self.is_dead = False
        self.is_winner = False

    def __repr__(self) -> str:
        """
        :return: a String to represent this player
        """
        return f"[Player {self.name} with ${self.coins} using {self.llm}]"

    def system_prompt(self) -> str:
        """
        :return: a System Prompt to be sent to the LLM
        """
        other_names = [other.name for other in self.others]
        return instructions(self.name, other_names)

    def user_prompt(self, turn: int) -> str:
        """
        :return: a User prompt to instruct the LLM for this player for this turn
        """
        other_names = [other.name for other in self.others]
        other_coins = [other.coins for other in self.others]
        return prompt(
            self.name, other_names, other_coins, self.coins, turn, self.records
        )

    def make_move(self, turn: int) -> str:
        """
        Carry out a turn by interfacing with my LLM
        :param turn: which turn number we are on
        :return: the response from the LLM
        """
        system_prompt = self.system_prompt()
        user_prompt = self.user_prompt(turn)
        return self.llm.send(system_prompt, user_prompt, self.MAX_TOKENS)

    def report(self) -> str:
        """
        Create a report of this player
        :return:
        """
        result = f"Player name: {self.name}<br/>"
        result += f"Model: {self.llm.model_name}<br/>"
        result += f"Temperature: {self.llm.temperature}<br/><br/>"
        for turn_record in self.records:
            result += str(turn_record).replace("\n", "<br/>")
            result += "<br/>"
        return result

    def kill(self) -> None:
        """
        This player has died - update the status
        """
        self.is_dead = True
