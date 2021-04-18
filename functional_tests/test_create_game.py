import re
from typing import Callable

from fastapi import status
from fastapi.testclient import TestClient
from requests.models import Response

from main import app


def test_create_game_success():
    is_uuid4: Callable = lambda s: bool(
        re.match(
            '^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
            s,
        )
    )
    with TestClient(app) as test_client:
        res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo', 'bar'],
                'columns': 4,
                'rows': 4,
            },
        )
        game_id: str = res.json()['gameId']
        assert res.status_code == status.HTTP_200_OK
        assert is_uuid4(game_id)

def test_create_game_invalid_number_of_players():
    with TestClient(app) as test_client:
        res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo'],
                'columns': 4,
                'rows': 4,
            },
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert res.json() == {
            'detail': [
                {
                    'loc': ['body', 'players'],
                    'msg': 'must be length 2',
                    'type': 'value_error',
                },
            ],
        }

def test_create_game_players_not_distinct():
    with TestClient(app) as test_client:
        res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo', 'foo'],
                'columns': 4,
                'rows': 4,
            },
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert res.json() == {
            'detail': [
                {
                    'loc': ['body', 'players'],
                    'msg': 'all entries must be distinct',
                    'type': 'value_error',
                },
            ],
        }

def test_create_game_dimensions_incomplete():
    with TestClient(app) as test_client:
        res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo', 'bar'],
                'columns': 4,
            },
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert res.json() == {
            'detail': [
                {
                    'loc': ['body', 'rows'],
                    'msg': 'field required',
                    'type': 'value_error.missing',
                },
            ]
        }

def test_create_game_invalid_dimensions():
    with TestClient(app) as test_client:
        res: Response = test_client.post(
            '/drop_token',
            json={
                'players': ['foo', 'bar'],
                'columns': 4,
                'rows': 0,
            },
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert res.json() == {
            'detail': [
                {
                    'loc': ['body', 'rows'],
                    'msg': 'must be greater than 0',
                    'type': 'value_error',
                },
            ]
        }
