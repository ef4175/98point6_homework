from fastapi import status
from fastapi.testclient import TestClient
from requests.models import Response

from main import app


def test_get_moves_on_nonexistent_game():
    with TestClient(app) as test_client:
        res: Response = test_client.get('drop_token/doesnt-exist/moves')
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert res.json() == {'detail': 'Game not found.'}

def test_get_moves_without_query_params_returns_all_moves():
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
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 1})
        get_moves_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves',
        )
        assert get_moves_res.status_code == status.HTTP_200_OK
        assert get_moves_res.json() == {
            'moves': [
                {'type': 'MOVE', 'player': 'foo', 'column': 3},
                {'type': 'MOVE', 'player': 'bar', 'column': 2},
                {'type': 'MOVE', 'player': 'foo', 'column': 0},
                {'type': 'MOVE', 'player': 'bar', 'column': 1},
            ],
        }

def test_get_moves_without_until_query_param():
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
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 1})
        get_moves_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves',
            params={'start': 1},
        )
        assert get_moves_res.status_code == status.HTTP_200_OK
        assert get_moves_res.json() == {
            'moves': [
                {'type': 'MOVE', 'player': 'bar', 'column': 2},
                {'type': 'MOVE', 'player': 'foo', 'column': 0},
                {'type': 'MOVE', 'player': 'bar', 'column': 1},
            ],
        }

def test_get_moves_without_start_query_param():
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
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 1})
        get_moves_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves',
            params={'until': 1},
        )
        assert get_moves_res.status_code == status.HTTP_200_OK
        assert get_moves_res.json() == {
            'moves': [
                {'type': 'MOVE', 'player': 'foo', 'column': 3},
                {'type': 'MOVE', 'player': 'bar', 'column': 2},
            ],
        }

def test_get_moves_with_start_and_until_query_params():
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
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 1})
        get_moves_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves',
            params={'start': 0, 'until': 2},
        )
        assert get_moves_res.status_code == status.HTTP_200_OK
        assert get_moves_res.json() == {
            'moves': [
                {'type': 'MOVE', 'player': 'foo', 'column': 3},
                {'type': 'MOVE', 'player': 'bar', 'column': 2},
                {'type': 'MOVE', 'player': 'foo', 'column': 0},
            ],
        }

def test_get_moves_with_start_equal_until():
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
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 1})
        get_moves_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves',
            params={'start': 1, 'until': 1},
        )
        assert get_moves_res.status_code == status.HTTP_200_OK
        assert get_moves_res.json() == {
            'moves': [
                {'type': 'MOVE', 'player': 'bar', 'column': 2},
            ],
        }

def test_get_moves_with_start_greater_than_until():
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
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 1})
        get_moves_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves',
            params={'start': 2, 'until': 1},
        )
        assert get_moves_res.status_code == status.HTTP_404_NOT_FOUND
        assert get_moves_res.json() == {'detail': 'Invalid range.'}

def test_get_moves_with_start_greater_than_or_equal_num_moves():
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
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 1})
        get_moves_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves',
            params={'start': 4},
        )
        assert get_moves_res.status_code == status.HTTP_404_NOT_FOUND
        assert get_moves_res.json() == {'detail': 'Invalid range.'}

def test_get_moves_with_until_less_than_0():
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
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 1})
        get_moves_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves',
            params={'until': -1},
        )
        assert get_moves_res.status_code == status.HTTP_404_NOT_FOUND
        assert get_moves_res.json() == {'detail': 'Invalid range.'}

def test_get_moves_unprocessable_query_params():
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
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 1})
        get_moves_res: Response = test_client.get(
            f'/drop_token/{game_id}/moves',
            params={'start': 'somewhere'},
        )
        assert get_moves_res.status_code == status.HTTP_400_BAD_REQUEST
        assert get_moves_res.json() == {
            'detail': [
                {
                    'loc': ['query', 'start'],
                    'msg': 'value is not a valid integer',
                    'type': 'type_error.integer',
                },
            ],
        }
