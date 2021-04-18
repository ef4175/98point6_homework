from typing import List

from pydantic import BaseModel, validator
from pydantic.main import ModelMetaclass


class Move(BaseModel):
    column: int

class NewGame(BaseModel):
    players: List[str]
    columns: int
    rows: int

    @validator('players')
    def players_has_configured_number_of_distinct_strings(
        cls: ModelMetaclass,
        players: List[str],
    ) -> List[str]:
        allowed_players_per_game: int = 2
        if len(players) != allowed_players_per_game:
            raise ValueError(f'must be length {allowed_players_per_game}')
        players_are_distinct: bool = len(players) == len(set(players))
        if not players_are_distinct:
            raise ValueError('all entries must be distinct')
        return players

    @validator('columns')
    def columns_is_greater_than_0(cls: ModelMetaclass, columns: int) -> int:
        if not columns > 0:
            raise ValueError('must be greater than 0')
        return columns

    @validator('rows')
    def rows_is_greater_than_0(cls: ModelMetaclass, rows: int) -> int:
        if not rows > 0:
            raise ValueError('must be greater than 0')
        return rows
