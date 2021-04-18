from fastapi import status
from fastapi.testclient import TestClient
from requests.models import Response

from main import app


def test_quit_on_nonexistent_game():
    with TestClient(app) as test_client:
        res: Response = test_client.delete(
            '/drop_token/invalid-game-id/some-player',
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert res.json() == {'detail': 'Game not found.'}

def test_quit_with_invalid_player():
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
        quit_res: Response = test_client.delete(
            f'/drop_token/{game_id}/nobody',
        )
        assert quit_res.status_code == status.HTTP_404_NOT_FOUND
        assert quit_res.json() == {'detail': 'Player not found.'}

def test_quit_success_then_failure():
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
        quit_res_1: Response = test_client.delete(
            f'/drop_token/{game_id}/foo',
        )
        quit_res_2: Response = test_client.delete(
            f'/drop_token/{game_id}/bar',
        )
        assert quit_res_1.status_code == status.HTTP_202_ACCEPTED
        assert quit_res_1.json() is None
        assert quit_res_2.status_code == status.HTTP_410_GONE
        assert quit_res_2.json() == {'detail': 'Game is done.'}
