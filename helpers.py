from typing import List


def check_winner(board: List[List[int]], target: int, how_many: int) -> bool:
    # Brute force O(r*c*k) check.
    # This can be optimized to O(k), k=how_many, using a sliding window trick.
    rows: int = len(board)
    cols: int = len(board[0])
    for box_row in range(rows - how_many + 1):
        for box_col in range(cols - how_many + 1):
            # Check all rows in this box
            for row in range(how_many):
                this_row: List[int] = (
                    board[box_row + row][box_col : box_col + how_many]
                )
                if all(value == target for value in this_row):
                    return True
            # Check all columns in this box
            for col in range(how_many):
                this_col: List[int] = [
                    board[box_row + i][box_col + col]
                    for i in range(how_many)
                ]
                if all(value == target for value in this_col):
                    return True
            # Check the diagonal with slope = -1
            downward_diagonal: List[int] = [
                board[box_row + i][box_col + i]
                for i in range(how_many)
            ]
            if all(value == target for value in downward_diagonal):
                return True
            # Check the diagonal with slope = 1
            upward_diagonal: List[int] = [
                board[box_row + how_many - i - 1][box_col + i]
                for i in range(how_many)
            ]
            if all(value == target for value in upward_diagonal):
                return True
    return False
