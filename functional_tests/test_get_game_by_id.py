from fastapi import status
from fastapi.testclient import TestClient
from requests.models import Response

from main import app


def test_get_game_with_nonexistent_id():
    with TestClient(app) as test_client:
        res: Response = test_client.get('/drop_token/foobar')
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert res.json() == {'detail': 'Game not found.'}

def test_get_game_that_is_in_progress():
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
        get_game_res: Response = test_client.get(f'/drop_token/{game_id}')
        assert get_game_res.status_code == status.HTTP_200_OK
        assert get_game_res.json() == {
            'players': ['foo', 'bar'],
            'state': 'IN_PROGRESS',
        }

def test_get_game_after_a_player_quits():
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
        test_client.delete(f'/drop_token/{game_id}/foo')
        get_game_res: Response = test_client.get(f'/drop_token/{game_id}')
        assert get_game_res.status_code == status.HTTP_200_OK
        assert get_game_res.json() == {
            'players': ['foo', 'bar'],
            'state': 'DONE',
            'winner': 'bar',
        }

def test_get_game_that_is_a_draw():
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

        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 1})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 3})

        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 1})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 3})

        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 1})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 3})

        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 1})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 3})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})

        '''
        Now the board will look like this
        [
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 1, 0, 1],
            [0, 1, 0, 1],
        ]
        '''

        get_game_res: Response = test_client.get(f'/drop_token/{game_id}')
        assert get_game_res.status_code == status.HTTP_200_OK
        assert get_game_res.json() == {
            'players': ['foo', 'bar'],
            'state': 'DONE',
            'winner': None,
        }

def test_get_game_with_a_winner():
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

        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 0})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 1})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})
        test_client.post(f'/drop_token/{game_id}/foo', json={'column': 1})
        test_client.post(f'/drop_token/{game_id}/bar', json={'column': 2})

        '''
        Now the board will look like this
        [
            [-1, -1, 1, -1],
            [-1, -1, 1, -1],
            [0, 0, 1, -1],
            [0, 0, 1, -1],
        ]
        '''

        get_game_res: Response = test_client.get(f'/drop_token/{game_id}')
        assert get_game_res.status_code == status.HTTP_200_OK
        assert get_game_res.json() == {
            'players': ['foo', 'bar'],
            'state': 'DONE',
            'winner': 'bar',
        }
