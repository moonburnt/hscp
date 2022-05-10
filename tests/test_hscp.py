import pytest

import hscp

url = "http://example.com"
app = "hyscores"
login = "asda"
pw = "352354300n00"
token = "324234efs42bt9ffon032r0frnd0fn"


@pytest.fixture
def client() -> hscp.HyScoresClient:
    return hscp.HyScoresClient(
        url=url,
        app=app,
    )


@pytest.fixture
def authorized_client(client):
    client.token = token
    return client


def test_client():
    client = hscp.HyScoresClient(
        url=url,
        app=app,
    )
    assert client.url == url
    assert client.app == app

    user_agent = "pytest_client"
    client = hscp.HyScoresClient(url=url, app=app, user_agent=user_agent)
    assert client.session.headers["user-agent"] == user_agent


def test_token_fail(client):
    with pytest.raises(hscp.TokenUnavailable):
        client.get_scores()


def test_register(requests_mock, client):
    requests_mock.post(url + "/register", json={"result": True})
    assert client.register(login, pw) is True


def test_login(requests_mock, client):
    requests_mock.post(url + "/login", json={"result": {"token": token}})
    client.login(login, pw)
    assert client.token is not None


def test_scores(requests_mock, authorized_client):
    requests_mock.get(url + "/scores", json={"result": []})
    assert isinstance(authorized_client.get_scores(), list)


def test_score(requests_mock, authorized_client):
    requests_mock.get(url + "/score", json={"result": {"sadam": 36}})
    assert isinstance(authorized_client.get_score("sadam"), dict)


def test_score_fail(requests_mock, authorized_client):
    requests_mock.get(url + "/score", json={"result": "Invalid Name"})
    with pytest.raises(hscp.InvalidName):
        authorized_client.get_score("your mom")


def test_score_uploader(requests_mock, authorized_client):
    requests_mock.post(url + "/score", json={"result": True})
    assert authorized_client.post_score("sadam", 69) is True


def test_logout(authorized_client):
    authorized_client.logout()
    assert authorized_client.token is None
