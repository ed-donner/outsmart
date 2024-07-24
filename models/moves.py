from pydantic import BaseModel, Field
from typing import Dict


class Move(BaseModel):

    strategy: str = Field(alias="secret strategy")
    give: str = Field(alias="give coin to")
    take: str = Field(alias="take coin from")
    messages: Dict[str, str] = Field(alias="private messages")
