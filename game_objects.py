from typing import Dict, List, Optional, Union

from exceptions import (
    ColumnFullException,
    ColumnOutOfBoundsException,
    FetchMoveException,
    GameCompletedException,
    IllegalTurnException,
    PlayerNotFoundException,
)
from helpers import check_winner
from payload_schema import NewGame


class TwoPlayerGame:
    def __init__(
        self,
        game_id: str,
        new_game: NewGame,
        win_condition: int,
    ) -> None:
        self.game_id: str = game_id
        self.moves: List[Dict[str, Union[int, str]]] = []
        self.original_players: List[str] = [*new_game.players]
        self.players: List[str] = [*new_game.players]
        self.state: str = 'IN_PROGRESS'
        self.winner: Optional[str] = None
        self.turn_index: int = 0
        self.board: List[List[int]] = [
            [*ref] for ref in ([[-1] * new_game.columns] * new_game.rows)
        ]
        self.row_index_of_lowest_empty_cell: List[int] = (
            [new_game.rows - 1] * new_game.columns
        )
        self.win_condition: int = win_condition

    def make_move(self, player: str, column: int) -> int:
        if player not in self.players:
            raise PlayerNotFoundException('Player not found.')

        if self.state == 'DONE':
            raise GameCompletedException('Game is done.')

        whose_turn: str = self.players[self.turn_index]
        if player != whose_turn:
            raise IllegalTurnException('Wait for other player to make a move.')

        num_columns: int = len(self.board[0])
        out_of_bounds: bool = column < 0 or column >= num_columns
        if out_of_bounds:
            raise ColumnOutOfBoundsException('Column out of bounds.')

        row_index_to_fill: int = self.row_index_of_lowest_empty_cell[column]
        num_rows: int = len(self.board)
        if row_index_to_fill < 0:
            raise ColumnFullException('Column is full.')

        self.board[row_index_to_fill][column] = self.turn_index
        move_number: int = len(self.moves)
        self.moves.append({
            'type': 'MOVE',
            'player': player,
            'column': column,
        })
        self.row_index_of_lowest_empty_cell[column] -= 1

        all_columns_are_full: bool = all(
            row_index < 0
            for row_index in self.row_index_of_lowest_empty_cell
        )
        if all_columns_are_full:
            self.state = 'DONE'

        if check_winner(self.board, self.turn_index, self.win_condition):
            self.state = 'DONE'
            self.winner = player

        self.turn_index = (self.turn_index + 1) % 2
        return move_number

    def get_moves(
        self,
        start: Optional[int] = None,
        until: Optional[int] = None,
    ) -> List[Dict[str, Union[int, str]]]:
        # Default start to 0 and until to end of moves
        slice_start: int = 0 if start is None else start
        slice_end: int = len(self.moves) if until is None else until + 1
        within_bounds: bool = slice_start >= 0 and slice_end <= len(self.moves)
        result_will_be_nonempty: bool = slice_start < slice_end
        can_slice: bool = within_bounds and result_will_be_nonempty
        if not can_slice:
            raise FetchMoveException('Invalid range.')
        slice_arg: slice = slice(slice_start, slice_end)
        moves_sublist: List[Dict[str, Union[int, str]]] = self.moves[slice_arg]
        return moves_sublist

    def get_move(self, move_index: int) -> Dict[str, Union[int, str]]:
        within_bounds: bool = move_index >= 0 and move_index < len(self.moves)
        if not within_bounds:
            raise FetchMoveException('Invalid move number.')
        return self.moves[move_index]

    def delete_player(self, player: str) -> None:
        if player not in self.players:
            raise PlayerNotFoundException('Player not found.')
        if self.state == 'DONE':
            raise GameCompletedException('Game is done.')
        self.moves.append({
            'type': 'QUIT',
            'player': player,
        })
        self.players = [p for p in self.players if p != player]
        self.state = 'DONE'
        self.winner = self.players[0]
