import os
import uuid
from typing import Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from exceptions import (
    ColumnFullException,
    ColumnOutOfBoundsException,
    FetchMoveException,
    GameCompletedException,
    IllegalTurnException,
    PlayerNotFoundException,
)
from payload_schema import Move, NewGame
from game_objects import TwoPlayerGame


games: Dict[str, TwoPlayerGame] = {}
app: FastAPI = FastAPI()

@app.on_event('shutdown')
def clear_in_memory_state():
    games.clear()

@app.exception_handler(RequestValidationError)
def override_fastapi_default_422_response_with_400_on_invalid_payloads(
    request: Request,
    exception: RequestValidationError,
) -> None:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': exception.errors()},
    )

@app.get('/drop_token')
def get_all_in_progress_games() -> JSONResponse:
    ids_of_games_in_progress: List[str] = [
        game_id for game_id in games if games[game_id].state == 'IN_PROGRESS'
    ]
    payload: Dict[str, List[str]] = {'games': ids_of_games_in_progress}
    return JSONResponse(content=payload)

@app.get('/drop_token/{game_id}')
def get_game(game_id: str) -> JSONResponse:
    if game_id not in games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Game not found.',
        )
    this_game: TwoPlayerGame = games[game_id]
    if this_game.state == 'DONE':
        payload: Dict[str, Union[List[str], str]] = {
            'players': this_game.original_players,
            'state': this_game.state,
            'winner': this_game.winner,
        }
        return JSONResponse(content=payload)
    payload: Dict[str, Union[List[str], str]] = {
        'players': this_game.original_players,
        'state': this_game.state,
    }
    return JSONResponse(content=payload)

@app.post('/drop_token')
def create_new_game(new_game: NewGame) -> JSONResponse:
    win_condition: int = int(os.environ['WIN_CONDITION'], 10)
    uuid_4: str = str(uuid.uuid4())
    games[uuid_4] = TwoPlayerGame(uuid_4, new_game, win_condition)
    payload: Dict[str, str] = {'gameId': uuid_4}
    return JSONResponse(content=payload)

@app.post('/drop_token/{game_id}/{player_id}')
def make_a_move(game_id: str, player_id: str, move: Move) -> JSONResponse:
    if game_id not in games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Game not found.',
        )
    this_game: TwoPlayerGame = games[game_id]
    try:
        move_number: int = this_game.make_move(player_id, move.column)
        payload: Dict[str, str] = {'move': f'{game_id}/moves/{move_number}'}
        return JSONResponse(content=payload)
    except PlayerNotFoundException as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{error}',
        )
    except IllegalTurnException as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{error}',
        )
    except (
        GameCompletedException,
        ColumnOutOfBoundsException,
        ColumnFullException,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{error}',
        )

@app.delete('/drop_token/{game_id}/{player_id}')
def player_quits(game_id: str, player_id: str) -> JSONResponse:
    if game_id not in games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Game not found.',
        )
    this_game: TwoPlayerGame = games[game_id]
    try:
        this_game.delete_player(player_id)
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED)
    except PlayerNotFoundException as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{error}',
        )
    except GameCompletedException as error:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=f'{error}',
        )

@app.get('/drop_token/{game_id}/moves')
def get_moves(
    game_id: str,
    start: Optional[int] = None,
    until: Optional[int] = None,
) -> JSONResponse:
    if game_id not in games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Game not found.',
        )
    this_game: TwoPlayerGame = games[game_id]
    try:
        moves_sublist: List[Dict[str, Union[int, str]]] = this_game.get_moves(
            start,
            until,
        )
        payload: Dict[str, List[Dict[str, Union[int, str]]]] = {
            'moves': moves_sublist,
        }
        return JSONResponse(content=payload)
    except FetchMoveException as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{error}',
        )

@app.get('/drop_token/{game_id}/moves/{move_number}')
def get_moves(game_id: str, move_number: int) -> JSONResponse:
    if game_id not in games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Game not found.',
        )
    this_game: TwoPlayerGame = games[game_id]
    try:
        move: Dict[str, Union[int, str]] = this_game.get_move(move_number)
        return JSONResponse(content=move)
    except FetchMoveException as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{error}',
        )
