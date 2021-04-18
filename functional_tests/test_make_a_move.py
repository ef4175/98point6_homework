from fastapi import status
from fastapi.testclient import TestClient
from requests.models import Response

from main import app


def test_post_move_on_nonexistent_game():
    with TestClient(app) as test_client:
        res: Response = test_client.post(
            '/drop_token/invalid-game-id/some-player',
            json={
                'column': 1,
            },
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert res.json() == {'detail': 'Game not found.'}

def test_post_move_with_empty_payload():
    with TestClient(app) as test_client:
        create_game_res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo', 'bar'],
                'columns': 4,
                'rows': 4,
            },
        )
        game_id: str = create_game_res.json()['gameId']
        post_move_res: Response = test_client.post(
            f'/drop_token/{game_id}/foo',
            json={}
        )
        assert post_move_res.status_code == status.HTTP_400_BAD_REQUEST
        assert post_move_res.json() == {
            'detail': [
                {
                    'loc': ['body', 'column'],
                    'msg': 'field required',
                    'type': 'value_error.missing',
                },
            ],
        }

def test_post_move_with_column_having_unprocessable_value():
    with TestClient(app) as test_client:
        create_game_res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo', 'bar'],
                'columns': 4,
                'rows': 4,
            },
        )
        game_id: str = create_game_res.json()['gameId']
        post_move_res: Response = test_client.post(
            f'/drop_token/{game_id}/foo',
            json={
                'column': 'lol',
            },
        )
        assert post_move_res.status_code == status.HTTP_400_BAD_REQUEST
        assert post_move_res.json() == {
            'detail': [
                {
                    'loc': ['body', 'column'],
                    'msg': 'value is not a valid integer',
                    'type': 'type_error.integer',
                },
            ],
        }

def test_post_move_with_out_of_bounds_columns():
    with TestClient(app) as test_client:
        create_game_res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo', 'bar'],
                'columns': 4,
                'rows': 4,
            },
        )
        game_id: str = create_game_res.json()['gameId']
        post_move1_res: Response = test_client.post(
            f'/drop_token/{game_id}/foo',
            json={
                'column': -1,
            },
        )
        post_move2_res: Response = test_client.post(
            f'/drop_token/{game_id}/foo',
            json={
                'column': 4,
            },
        )
        assert post_move1_res.status_code == status.HTTP_400_BAD_REQUEST
        assert post_move1_res.json() == {'detail': 'Column out of bounds.'}
        assert post_move2_res.status_code == status.HTTP_400_BAD_REQUEST
        assert post_move2_res.json() == {'detail': 'Column out of bounds.'}

def test_post_move_with_invalid_player():
    with TestClient(app) as test_client:
        create_game_res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo', 'bar'],
                'columns': 4,
                'rows': 4,
            },
        )
        game_id: str = create_game_res.json()['gameId']
        post_move_res: Response = test_client.post(
            f'/drop_token/{game_id}/nobody',
            json={
                'column': 1,
            },
        )
        assert post_move_res.status_code == status.HTTP_404_NOT_FOUND
        assert post_move_res.json() == {'detail': 'Player not found.'}

def test_post_move_on_wrong_turn():
    with TestClient(app) as test_client:
        create_game_res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo', 'bar'],
                'columns': 4,
                'rows': 4,
            },
        )
        game_id: str = create_game_res.json()['gameId']
        test_client.post(
            f'/drop_token/{game_id}/foo',
            json={
                'column': 1,
            },
        )
        second_move_res: Response = test_client.post(
            f'/drop_token/{game_id}/foo',
            json={
                'column': 1,
            },
        )
        assert second_move_res.status_code == status.HTTP_409_CONFLICT
        assert second_move_res.json() == {
            'detail': 'Wait for other player to make a move.',
        }

def test_post_move_when_column_is_full():
    with TestClient(app) as test_client:
        create_game_res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo', 'bar'],
                'columns': 4,
                'rows': 1,
            },
        )
        game_id: str = create_game_res.json()['gameId']
        test_client.post(
            f'/drop_token/{game_id}/foo',
            json={
                'column': 1,
            },
        )
        second_move_res: Response = test_client.post(
            f'/drop_token/{game_id}/bar',
            json={
                'column': 1,
            },
        )
        assert second_move_res.status_code == status.HTTP_400_BAD_REQUEST
        assert second_move_res.json() == {'detail': 'Column is full.'}

def test_post_move_after_game_is_done():
    with TestClient(app) as test_client:
        create_game_res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo', 'bar'],
                'columns': 4,
                'rows': 1,
            },
        )
        game_id: str = create_game_res.json()['gameId']
        test_client.delete(f'/drop_token/{game_id}/foo')
        move_res: Response = test_client.post(
            f'/drop_token/{game_id}/bar',
            json={
                'column': 1,
            },
        )
        assert move_res.status_code == status.HTTP_400_BAD_REQUEST
        assert move_res.json() == {'detail': 'Game is done.'}

def test_post_move_success():
    with TestClient(app) as test_client:
        create_game_res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo', 'bar'],
                'columns': 4,
                'rows': 4,
            },
        )
        game_id: str = create_game_res.json()['gameId']
        first_move_res: Response = test_client.post(
            f'/drop_token/{game_id}/foo',
            json={
                'column': 1,
            },
        )
        second_move_res: Response = test_client.post(
            f'/drop_token/{game_id}/bar',
            json={
                'column': 1,
            },
        )
        assert first_move_res.status_code == status.HTTP_200_OK
        assert first_move_res.json() == {'move': f'{game_id}/moves/0'}
        assert second_move_res.status_code == status.HTTP_200_OK
        assert second_move_res.json() == {'move': f'{game_id}/moves/1'}
