import os
import streamlit as st
import pymongo
from typing import List, Self, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import pandas as pd
import trueskill
from trueskill import Rating
import json


class Result(BaseModel):
    """
    An individual result of 1 LLM playing in a game, capturing how many coins it ended with
    and its rank, where 0 means that it won
    """

    name: str
    llm: str
    coins: int
    rank: int

    def __repr__(self) -> str:
        """
        Convert this object to json
        :return: a json string for each result
        """
        return json.dumps(self.model_dump())

    def update_on(self, df: pd.DataFrame) -> None:
        """
        Add this result to the DataFrame for the leaderboard
        This is perhaps more complex than needed because the dataframe only has Win %, not a count of Wins
        :param df: the dataframe for the leaderboard
        """
        llm = self.llm
        if not (df["LLM"] == llm).any():
            df.loc[len(df)] = [llm, 0, 0.0, 0.0]
        games = df.loc[df["LLM"] == llm, "Games"].values[0]
        wins_percent = df.loc[df["LLM"] == llm, "Win %"].values[0]
        wins = games * wins_percent / 100
        df.loc[df["LLM"] == llm, "Games"] += 1
        if self.rank == 0:
            df.loc[df["LLM"] == llm, "Win %"] = (wins + 1) * 100 / (games + 1)
        else:
            df.loc[df["LLM"] == llm, "Win %"] = wins * 100 / (games + 1)


class Game(BaseModel):
    """
    The result of a Game, stored in the DB
    """

    run_date: datetime
    results: List[Result]

    def __str__(self) -> str:
        """
        :return: a string json version of this game
        """
        return json.dumps(self.model_dump())

    @staticmethod
    @st.cache_resource
    def get_connection():
        mongo_uri = os.getenv("MONGO_URI")
        return pymongo.MongoClient(mongo_uri)

    @classmethod
    @st.cache_data(ttl=1)
    def all(cls) -> List[Self]:
        client = cls.get_connection()
        games = client.outsmart.games
        docs = list(games.find())
        return [Game(**doc) for doc in docs]

    def save(self):
        client = self.get_connection()
        games = client.outsmart.games
        games.insert_one(self.model_dump())

    @classmethod
    @st.cache_data(ttl=1)
    def count(cls) -> int:
        client = cls.get_connection()
        return client.outsmart.games.count_documents({})

    @classmethod
    @st.cache_data(ttl=2)
    def reset(cls):
        client = cls.get_connection()
        client.outsmart.games.delete_many({})

    @classmethod
    @st.cache_data(ttl=1)
    def latest(cls, k: int) -> List[Self]:
        client = cls.get_connection()
        games = client.outsmart.games
        latest = games.find().sort({"run_date": -1}).limit(k)
        return [Game(**each) for each in latest]

    @classmethod
    def ratings_for(cls, games: List[Self], df: pd.DataFrame) -> Dict[str, Rating]:
        """
        Create a Rating object for each LLM in the list of historic games
        :param games: a list of historic games
        :param df: a dataframe with the ranks of past games
        :return: a dictionary that maps models to their Rating objects
        """
        ratings = {row["LLM"]: Rating() for _, row in df.iterrows()}
        for game in games:
            llms = [result.llm for result in game.results]
            rating_groups = [(ratings[llm],) for llm in llms]
            ranks = [result.rank for result in game.results]
            rated = trueskill.rate(rating_groups, ranks=ranks)
            for index, llm in enumerate(llms):
                ratings[llm] = rated[index][0]
        return ratings

    @classmethod
    def games_df(cls) -> pd.DataFrame:
        """
        Create a dataframe that represents the leaderboard for games played
        Use the TrueSkill methodology to assess Skill level
        The expose method calculates 1 number (mean - 3 * standard deviation) for the leaderboard
        :return: a DataFrame with the leaderboard including Win % and Skill
        """
        columns = ["LLM", "Games", "Win %", "Skill"]
        df = pd.DataFrame(columns=columns)
        games = cls.all()
        for game in games:
            for result in game.results:
                result.update_on(df)
        ratings = cls.ratings_for(games, df)
        for llm, rating in ratings.items():
            df.loc[df["LLM"] == llm, "Skill"] = trueskill.expose(rating)
        return df

    @classmethod
    def latest_df(cls) -> pd.DataFrame:
        """
        Create a table of the most recent 5 games
        :return: A dataframe to represent the winners of the last 5 games
        """
        columns = ["When", "Winner(s)"]
        df = pd.DataFrame(columns=columns)
        for game in cls.latest(5):
            when = game.run_date
            winners = [result.llm for result in game.results if result.rank == 0]
            winners_str = ", ".join(winners)
            df.loc[len(df)] = [when, winners_str]
        return df
