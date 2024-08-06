from typing import List, Dict, Callable
import json
import logging
from game.players import Player
from models.moves import Move
from models.records import TurnRecord
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[float, str], None]


class Referee:

    players: List[Player]
    turn: int
    records: Dict[str, TurnRecord]
    player_names = List[str]
    player_map: Dict[str, Player]
    alliances = List[str]

    def __init__(self, players: List[Player], turn: int):
        """
        Initialize this instance
        :param players: list of players
        :param turn: turn number
        """
        self.players = players
        self.turn = turn
        self.records = {}
        self.player_names = [player.name for player in players]
        self.player_map = {player.name: player for player in players}
        self.alliances = []

    def do_turn_for_player(self, player: Player) -> TurnRecord:
        """
        Carry out a turn for this player whilst handling any exceptions raised
        :param player: the player being processed
        :return: a TurnRecord that wraps the output from the model, including whether it was valid
        """
        response = ""
        try:
            response = player.make_move(self.turn)
            move = self.parse_response(response)
            logger.info(f"Turn {self.turn} received OK from {player}")
            return TurnRecord(player.name, self.turn, move=move)
        except Exception as e:
            logger.error(f"Exception while processing response from {player}")
            logger.error(e)
            logger.error(f"Response received was:\n{response}")
            return TurnRecord(player.name, self.turn, is_invalid_move=True)

    def player_with_name(self, name: str) -> Player:
        """
        Return the player with the given name
        :param name: the name of a player
        :return: the player object
        """
        player = self.player_map[name]
        if player:
            return player
        else:
            raise ValueError(f"Failed to find player with name {name}")

    def do_turn(self, progress: ProgressCallback) -> None:
        """
        This is called by an Arena object to run a Turn
        First get each Player to make a move using ThreadPoolExecutor to run in parallel
        Then evaluate each Player in turn
        :param progress: a callback on which to report progress that will be reflected in the UI
        :return:
        """
        progress(0, "Players are thinking..")
        responded = []
        with ThreadPoolExecutor(max_workers=len(self.players)) as e:
            for record in e.map(self.do_turn_for_player, self.players):
                player = self.player_with_name(record.name)
                responded.append(record.name)
                prog = len(responded) / len(self.players)
                progress(prog, f"{', '.join(responded)} responded..")
                self.records[record.name] = record
                player.records.append(record)
        progress(1.0, "Finishing up..")
        self.handle_turn()

    def handle_turn(self) -> None:
        """
        The turn has happened; now go through each player and make the trades
        """
        self.handle_giving()
        self.handle_taking()
        self.handle_alliances()
        self.handle_messages()

    def handle_giving(self) -> None:
        """
        Go through the players and give a coin for each of the people they gave to
        """
        for player in self.players:
            record = self.records[player.name]
            if not record.is_invalid_move:
                who = record.move.give
                self.player_map[who].coins += 1
                self.records[who].givers.append(player.name)
            player.coins -= 1

    def handle_taking(self) -> None:
        """
        Go through the players and take away a coin from people they've taken
        """
        for player in self.players:
            record = self.records[player.name]
            if not record.is_invalid_move:
                who = record.move.take
                self.player_map[who].coins -= 1
                self.records[who].takers.append(player.name)
                player.coins += 1

    def handle_alliances(self) -> None:
        """
        Identify the special situation of an alliance, where 2 players have picked each other
        and have taken from the same player
        """
        for player in self.players:
            name1 = player.name
            record1 = self.records[name1]
            if not record1.is_invalid_move:
                name2 = record1.move.give
                record2 = self.records[name2]
                if (
                    not record2.is_invalid_move
                    and record2.move.give == name1
                    and (name1 not in self.alliances)
                    and (name2 not in self.alliances)
                ):
                    self.investigate_alliance(name1, record1, name2, record2)

    def investigate_alliance(
        self, name1: str, record1: TurnRecord, name2: str, record2: TurnRecord
    ) -> None:
        """
        We know that these 2 players have gifted each other.
        See if they took from the same player
        """
        take1 = record1.move.take
        take2 = record2.move.take
        if take1 == take2:
            self.alliances.append(name1)
            self.alliances.append(name2)
            self.process_alliance(name1, name2, take1)

    def process_alliance(self, name1: str, name2: str, victim: str) -> None:
        """
        We have an alliance - now take action
        """
        self.player_map[name1].coins += 1
        self.player_map[name2].coins += 1
        self.player_map[victim].coins -= 2
        self.records[name1].alliances_with.append(name2)
        self.records[name2].alliances_with.append(name1)
        self.records[victim].alliances_against.extend([name1, name2])

    def handle_messages(self) -> None:
        """
        Manage the messages that each player has sent - put it in the recipient's records
        """
        for player in self.players:
            name = player.name
            record = self.records[name]
            if not record.is_invalid_move:
                messages = record.move.messages
                for recipient, message in messages.items():
                    self.records[recipient].messages[player.name] = message

    def check_response(self, move: Move) -> None:
        """
        Make sure the give and take fields are valid, otherwise fail
        :param move: The move object representing the response from the player
        """
        if move.give not in self.player_names:
            raise ValueError("Invalid give field in the response JSON")
        if move.take not in self.player_names:
            raise ValueError("Invalid take field in the response JSON")
        if move.give == move.take:
            raise ValueError("Illegal response JSON: matching give and take")

    def parse_response(self, response: str) -> Move:
        """
        Convert a text response into a Move object
        :param response: the text returned from an LLM
        :return: a Move object
        """
        first = response.find("{")
        last = response.rfind("}")
        response = response[first : last + 1]
        response_dict = json.loads(response)
        move = Move(**response_dict)
        self.check_response(move)
        return move
