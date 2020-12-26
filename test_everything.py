import datetime
import os
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from auth.security import JAM, oauth2_scheme
from distribution.models import MusicDistribution
from main import app
import auth.models


@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    with mock.patch.dict(os.environ, {"PROJECT_KEY": "1234"}):
        yield


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def authenticated_client(monkeypatch, test_client):
    # verify token is tested elsewhere, ignore it an return some claims
    async def _fake_claims(*_args, **_kwargs):
        return {"header": "header"}, {"email": "test@example.com"}

    # get a fake user to return from authentication flow
    async def _fake_user(email):
        return auth.models.User(
            name="Test User", email=email, admin=False, disabled=False
        )

    # if there is no cookie, this will raise, so it just needs to return something.
    monkeypatch.setattr(oauth2_scheme, "__call__", lambda *args: "12344")
    monkeypatch.setattr(JAM, "verify_token", _fake_claims)
    monkeypatch.setattr("auth.models.get_user_by_email", _fake_user)
    return test_client


@pytest.fixture
def dist1_data():
    return {
        "key": "id0",
        "student": "Michael Burnham",
        "pieces": [
            {"title": "Serenade for Strings", "composer": "P. Tchaikovsky"},
            {"title": "St. Paul's Suite", "composer": "G. Holst"},
        ],
        "distribution_method": "Mail",
        "date": str(datetime.date.today()),
        "parts": ["Violin 1", "Violin 2"],
    }


@pytest.fixture
def dist1(dist1_data):
    return MusicDistribution.parse_obj(dist1_data)


@pytest.fixture
def dist2_data():
    return {
        "key": "id1",
        "student": "Sylvia Tilly",
        "pieces": [
            {"title": "Serenade for Strings", "composer": "P. Tchaikovsky"},
            {"title": "St. Paul's Suite", "composer": "G. Holst"},
        ],
        "distribution_method": "Mail",
        "date": str(datetime.date.today()),
        "parts": ["Cello"],
    }


@pytest.fixture
def dist2(dist2_data):
    return MusicDistribution.parse_obj(dist2_data)


def test_distributions_not_logged_in(test_client):
    response = test_client.get("/distributions")
    assert response.status_code == 401


def test_get_distributions_all_single_dist(
    authenticated_client, monkeypatch, dist1, dist1_data
):
    def _fake_distributions():
        return [dist1]

    monkeypatch.setattr(MusicDistribution, "get_all", _fake_distributions)
    response = authenticated_client.get("/distributions")
    assert response.status_code == 200
    assert dist1_data in response.json()


def test_get_distributions_all_multiple(
    authenticated_client, monkeypatch, dist1, dist1_data, dist2, dist2_data
):
    def _fake_distributions():
        return [dist1, dist2]

    monkeypatch.setattr(MusicDistribution, "get_all", _fake_distributions)
    response = authenticated_client.get("/distributions")
    assert response.status_code == 200
    assert dist1_data in response.json()
    assert dist2_data in response.json()
