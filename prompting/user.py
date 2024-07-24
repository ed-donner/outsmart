from typing import List
from models.records import TurnRecord


def first_turn(name: str, other_names: List[str], coins: int) -> str:
    """
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
    #     response += (
    #         """Here is another example of correctly formatted JSON:
    # {
    #     "secret strategy": "Your secret plans go here",
    #     "give coin to": "must be one of """
    #         + others
    #         + """",
    #     "take coin from": "must be one of """
    #         + others
    #         + """",
    #     "private messages":
    #     {
    # """
    #     )
    #     lines = [
    #         f'      "{other}": "Your private message for {other}"' for other in other_names
    #     ]
    #     response += ",\n".join(lines)
    #     response += """
    #     }
    # }
    #
    # """
    response += """You must only respond in JSON.
Your goal is to make most coins through strategy and negotiation."""
    return response


def for_turn(
    name: str, other_names: List[str], coins: int, turn: int, records: List[TurnRecord]
) -> str:
    """
    :return: a prompt that can be used for a first round user prompt
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
Please make your next move, by deciding which player to give a coin to, which player to take a coin from, and private messages for each player.
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
    #     response += (
    #         """Here is another example of correctly formatted JSON:
    # {
    #     "secret strategy": "Your secret plans go here",
    #     "give coin to": "must be one of """
    #         + others
    #         + """",
    #     "take coin from": "must be one of """
    #         + others
    #         + """",
    #     "private messages":
    #     {
    # """
    #     )
    #     lines = [
    #         f'      "{other}": "Your private message for {other}"' for other in other_names
    #     ]
    #     response += ",\n".join(lines)
    #     response += """
    #     }
    # }
    #
    # """
    # response += "You must only respond in JSON. Your goal is to make the most coins through strategy and negotiation."
    return response


def prompt(
    name: str, other_names: List[str], coins: int, turn: int, records: List[TurnRecord]
) -> str:
    if turn == 1:
        return first_turn(name, other_names, coins)
    else:
        return for_turn(name, other_names, coins, turn, records)
