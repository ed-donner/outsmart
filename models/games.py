import os
import streamlit as st
import pymongo
from typing import List, Self, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import pandas as pd


class Result(BaseModel):

    name: str
    llm: str
    coins: int
    rank: int

    def __repr__(self):
        return str(self.model_dump())


class Game(BaseModel):

    run_date: datetime
    results: List[Result]

    def __str__(self) -> str:
        return str(self.model_dump())

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
        rows = list(games.find())
        return [Game(**row) for row in rows]

    def save(self):
        client = self.get_connection()
        games = client.outsmart.games
        games.insert_one(self.model_dump())

    @classmethod
    @st.cache_data(ttl=1)
    def count(cls) -> int:
        client = cls.get_connection()
        return client.outsmart.games.count_documents()

    @classmethod
    def games_df(cls) -> pd.DataFrame:
        columns = ["LLM", "Games", "Win %", "Skill"]
        df = pd.DataFrame(columns=columns)
        for game in cls.all():
            for result in game.results:
                llm = result.llm
                if not (df["LLM"] == llm).any():
                    df.loc[len(df)] = [llm, 0, 0, 0]
                df.loc[df["LLM"] == llm, "Games"] += 1
        return df
