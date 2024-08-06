---
title: Outsmart
emoji: 🧠
colorFrom: yellow
colorTo: red
python_version: 3.11
sdk: streamlit
sdk_version: 1.36.0
app_file: app.py
pinned: false
license: mit
fullWidth: true
header: mini
tags: ["arena", "benchmark", "leaderboard"]
thumbnail: https://edwarddonner.com/wp-content/uploads/2024/08/outsmart.jpg
---

# Outsmart
### A battle of diplomacy and deviousness between LLMs

Outsmart is an LLM Arena that pits AI models against each other
in a game of strategy and negotiation.

[Play the game](https://edwarddonner.com/outsmart/)  
[Read the backstory](https://edwarddonner.com/2024/08/06/outsmart/) on my website  
[Clone the repo](https://github.com/ed-donner/outsmart) to use your API keys and fight with frontier models!

## Rules of the Game

1. Each player starts with 12 coins
2. With each turn:
- Players send private messages to all other players to hatch plans
- Players select to give 1 coin to 1 player, and take 1 coin from another player
- If 2 players give each other coins, and both take from the same player, that is considered an "alliance" and they each receive an additional coin, taken from the player that they ganged up on
3. The objective is to negotiate with the other players and make coins. The winner is the player with the most coins when one player goes bankrupt, or after 10 turns.

## Using the Arena

- Press the **Run Turn** button to see the LLMs make a move
- Open the **Inner Thoughts** expander if you want to see their memory logs
- Press the **Run Game** button to run all moves until the game is over
- Expand the left hand sidebar to see LLM rankings from all games
- For the public version, only lower cost LLMs are available to compete, otherwise **I** might go bankrupt! Follow the instructions below to run locally and try larger models.

## Installing locally

Using Anaconda is highly recommended, to provide you with a consistent environment including the right python version.

1. If you don't have it already, install [Anaconda](https://docs.anaconda.com/anaconda/install/)
2. Create and activate your environment with:  
`conda create -n outsmart python=3.11`  
`conda activate outsmart`
3. git clone the repo and install dependencies from the root directory:  
`pip install -r requirements.txt`
4. Create a .env file in the root directory and populate it with the following keys:  
```
GOOGLE_API_KEY=xxxx  
ANTHROPIC_API_KEY=xxxx  
OPENAI_API_KEY=xxxx  
ARENA=random
```
5. From the root directory, start streamlit to run the app!  
`python -m streamlit run app.py`

If you have problems, please do get in touch - I'd love to help!  
I'm at ed [at] edwarddonner [dot] com.

