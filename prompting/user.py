from typing import List
from models.records import TurnRecord


def first_turn(name: str, other_names: List[str], coins: int) -> str:
    """
    :param name: the name of the player
    :param other_names: the name of the competitors
    :param coins: how many coins the player has
    :return: a prompt that can be used for a first round user prompt
    """
    others = ", ".join(other_names)
    response = f"""Your player name is {name} and the other players are {others}.

This is the first turn of the game. There have been no interactions between any players yet, and no coins exchanged.
You have {coins} coins.
Please make your first move, by deciding which player to give a coin to, which player to take a coin from, and private messages for each player.
You must respond strictly in JSON, and it must follow this format:

"""
    response += (
        """{
    "secret strategy": "Here you should secretly explain your plans, for your own benefit - the other players will not see this",
    "give coin to": "Here you should put the player you will give a coin to; must be one of """
        + others
        + """",
    "take coin from": "Here you should put the player you will take a coin from; must be one of """
        + others
        + """",
    "private messages":
    {
"""
    )
    lines = [
        f'      "{other}": "Here you should put a private message for {other}"'
        for other in other_names
    ]
    response += ",\n".join(lines)
    response += """
    }
}

"""
    response += """You must only respond in JSON.
Your goal is to make most coins through strategy and negotiation."""
    return response


def for_turn(
    name: str,
    other_names: List[str],
    other_coins: List[int],
    coins: int,
    turn: int,
    records: List[TurnRecord],
) -> str:
    """
    :param name: the name of this player
    :param other_names: the names of its competitors
    :param other_coins: the coins of the competitors
    :param coins: this player's coins
    :param turn: the turn number
    :param records: the records of prior turns, to explain how we got here
    :return: a user prompt to get the LLM to make this move
    """
    others = ", ".join(other_names)
    response = f"""Your player name is {name} and the other players are {others}.

This is turn {turn} of the game. Here is a summary of you moves and the outcomes so far.

"""
    for record in records:
        response += str(record)

    response += f"""
That brings us to the current turn, {turn}.
As a result of the previous turns, you now have {coins} coins.
Here are the coins now held by the others. Your goal is to rank as high as possible compared to them.\n"""
    for other_name, other_coin in zip(other_names, other_coins):
        response += f"- {other_name} has {other_coin} coins\n"
    response += """Please make your next move, by deciding which player to give a coin to, which player to take a coin from, and private messages for each player.
You must respond strictly in JSON, and it must follow this format:

"""
    response += (
        """{
    "secret strategy": "Here you should secretly explain your plans, for your own benefit - the other players will not see this",
    "give coin to": "Here you should put the player you will give a coin to; must be one of """
        + others
        + """",
    "take coin from": "Here you should put the player you will take a coin from; must be one of """
        + others
        + """",
    "private messages":
    {
"""
    )
    lines = [
        f'      "{other}": "Here you should put a private message for {other}"'
        for other in other_names
    ]
    response += ",\n".join(lines)
    response += """
    }
}

"""
    return response


def prompt(
    name: str,
    other_names: List[str],
    other_coins: List[int],
    coins: int,
    turn: int,
    records: List[TurnRecord],
) -> str:
    """
    Decide how to prompt the LLM for this turn; use a different approach for Turn 1 and for subsequent Turns
    :param name: the name of this player
    :param other_names: the names of its competitors
    :param other_coins: the coins of the competitors
    :param coins: this player's coins
    :param turn: the turn number
    :param records: the records of prior turns, to explain how we got here
    :return: a user prompt to get the LLM to make this move
    """
    if turn == 1:
        return first_turn(name, other_names, coins)
    else:
        return for_turn(name, other_names, other_coins, coins, turn, records)
