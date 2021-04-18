from fastapi import status
from fastapi.testclient import TestClient
from requests.models import Response

from main import app


def test_get_games_when_there_are_none():
    with TestClient(app) as test_client:
        res: Response = test_client.get('/drop_token')
        assert res.status_code == status.HTTP_200_OK
        assert res.json() == {'games': []}

def test_get_games_after_one_is_created_and_after_a_player_quits():
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
        get_games_res_1: Response = test_client.get('/drop_token')
        assert get_games_res_1.status_code == status.HTTP_200_OK
        assert get_games_res_1.json() == {'games': [game_id]}
        test_client.delete(f'/drop_token/{game_id}/foo')
        get_games_res_2: Response = test_client.get('/drop_token')
        assert get_games_res_2.status_code == status.HTTP_200_OK
        assert get_games_res_2.json() == {'games': []}

def test_get_games_after_one_is_created_and_after_it_is_a_draw():
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
        get_games_res_1: Response = test_client.get('/drop_token')
        assert get_games_res_1.status_code == status.HTTP_200_OK
        assert get_games_res_1.json() == {'games': [game_id]}

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

        get_games_res_2: Response = test_client.get('/drop_token')
        assert get_games_res_2.status_code == status.HTTP_200_OK
        assert get_games_res_2.json() == {'games': []}

def test_get_games_after_one_is_created_and_after_a_player_wins():
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
        get_games_res_1: Response = test_client.get('/drop_token')
        assert get_games_res_1.status_code == status.HTTP_200_OK
        assert get_games_res_1.json() == {'games': [game_id]}

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

        get_games_res_2: Response = test_client.get('/drop_token')
        assert get_games_res_2.status_code == status.HTTP_200_OK
        assert get_games_res_2.json() == {'games': []}
