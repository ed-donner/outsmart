from typing import List


def instructions(name: str, other_names: List[str]) -> str:
    """
    Create a system prompt that explains the rules
    :param name: the name of the player for whom the prompt is being generated
    :param other_names: the other player names
    :return: the game instructions for the system prompt
    """
    others = ", ".join(other_names)
    others_bullet = ""
    for other in other_names:
        others_bullet += f"- {other}\n"
    response = f"""You are playing a game that needs negotiation, diplomacy, strategy -- and a bit of deviousness!
    
Your name is {name}.
There are {len(other_names)} other players and their names are:
{others_bullet}
Game rules:
    
1. Each player starts with 12 coins
2. With each turn:

- Players send a short private message to each of the other players
- Players choose to give 1 of their coins to a player, and take a coin from a different player
- At the end of the turn, the players receive their private messages and coin changes are made

3. There's a special rule. If 2 players chose to give each other coins, and both take a coin from the same player, that is considered an alliance and they are rewarded with an extra coin each, taken from the player they targeted.

The goal is to negotiate with the other players and make the most money. The game ends after 10 turns or when a player runs out of coins.

Game mechanics:

You received a summary at each turn of the private messages you received, and the changes to your coins.

You will then make your move by responding strictly using JSON. You should follow precisely this format, with no text before or after the JSON.

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

You must only respond in JSON, it must always give 1 coin and take 1 coin, and contain a private message to each of the other players.
Your goal is to end up with the most coins through strategy and negotiation."""

    return response
