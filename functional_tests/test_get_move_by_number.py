from fastapi import status
from fastapi.testclient import TestClient
from requests.models import Response

from main import app


def test_get_moves_on_nonexistent_game():
    with TestClient(app) as test_client:
        res: Response = test_client.get('drop_token/doesnt-exist/moves/1')
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert res.json() == {'detail': 'Game not found.'}

def test_get_move_number_too_small():
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
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 3})
        get_move_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves/-1',
        )
        assert get_move_res.status_code == status.HTTP_404_NOT_FOUND
        assert get_move_res.json() == {'detail': 'Invalid move number.'}

def test_get_move_number_too_large():
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
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 3})
        get_move_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves/1',
        )
        assert get_move_res.status_code == status.HTTP_404_NOT_FOUND
        assert get_move_res.json() == {'detail': 'Invalid move number.'}

def test_get_move_number_success():
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
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 3})
        get_move_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves/0',
        )
        assert get_move_res.status_code == status.HTTP_200_OK
        assert get_move_res.json() == {
            'type': 'MOVE',
            'player': 'foo',
            'column': 3,
        }

def test_get_move_number_with_unprocessable_value():
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
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 3})
        get_move_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves/haha',
        )
        assert get_move_res.status_code == status.HTTP_400_BAD_REQUEST
        assert get_move_res.json() == {
            'detail': [
                {
                    'loc': ['path', 'move_number'],
                    'msg': 'value is not a valid integer',
                    'type': 'type_error.integer',
                },
            ],
        }
