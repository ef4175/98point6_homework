from typing import List, Tuple
from unittest import TestCase

from helpers import check_winner


class HelpersTest(TestCase):
    def test_check_winner_0_has_a_winning_row(self) -> None:
        board: List[List[int]] = [
            [-1, -1, -1, -1],
            [-1, -1, -1, -1],
            [1, 1, 1, -1],
            [0, 0, 0, 0],
        ]
        self.assertTrue(check_winner(board, 0, 4))
        self.assertFalse(check_winner(board, 1, 4))

    def test_check_winner_0_has_a_winning_col(self) -> None:
        board: List[List[int]] = [
            [-1, -1, -1, 0],
            [-1, -1, 1, 0],
            [-1, -1, 1, 0],
            [-1, -1, 1, 0],
        ]
        self.assertTrue(check_winner(board, 0, 4))
        self.assertFalse(check_winner(board, 1, 4))

    def test_check_winner_0_has_a_winning_downward_diagonal(self) -> None:
        board: List[List[int]] = [
            [0, -1, -1, -1],
            [1, 0, -1, -1],
            [0, 1, 0, 0],
            [1, 1, 1, 0],
        ]
        self.assertTrue(check_winner(board, 0, 4))
        self.assertFalse(check_winner(board, 1, 4))

    def test_check_winner_0_has_a_winning_upward_diagonal(self) -> None:
        board: List[List[int]] = [
            [-1, -1, -1, 0],
            [-1, -1, 0, 1],
            [0, 0, 1, 0],
            [0, 1, 1, 1],
        ]
        self.assertTrue(check_winner(board, 0, 4))
        self.assertFalse(check_winner(board, 1, 4))

    def test_check_winner_no_one_won(self) -> None:
        board: List[List[int]] = [
            [-1, -1, -1, -1],
            [-1, -1, -1, -1],
            [-1, -1, -1, -1],
            [-1, -1, -1, -1],
        ]
        self.assertFalse(check_winner(board, 0, 4))
        self.assertFalse(check_winner(board, 1, 4))
