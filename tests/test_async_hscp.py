import asyncio
import pytest
import pytest_asyncio

import hscp

from aioresponses import aioresponses

url = "http://example.com"
app = "hyscores"
login = "asda"
pw = "352354300n00"
token = "324234efs42bt9ffon032r0frnd0fn"


@pytest_asyncio.fixture
async def client() -> hscp.HyScoresAsyncClient:
    client = hscp.HyScoresAsyncClient(
        url=url,
        app=app,
    )
    yield client
    await client.session.close()


@pytest.fixture
def authorized_client(client):
    client.token = token
    return client


@pytest.mark.asyncio
async def test_client():
    client = hscp.HyScoresAsyncClient(
        url=url,
        app=app,
    )
    assert client.url == url
    assert client.app == app
    await client.session.close()

    user_agent = "pytest_client"
    client = hscp.HyScoresAsyncClient(url=url, app=app, user_agent=user_agent)

    assert client.session.headers["user-agent"] == user_agent
    await client.session.close()


@pytest.mark.asyncio
async def test_token_fail(client):
    with pytest.raises(hscp.TokenUnavailable):
        await client.get_scores()


@pytest.mark.asyncio
async def test_register(client):
    with aioresponses() as m:
        m.post(url + "/register", payload={"result": True})
        resp = await client.register(login, pw)

        assert resp is True


@pytest.mark.asyncio
async def test_login(client):
    with aioresponses() as m:
        m.post(url + "/login", payload={"result": {"token": token}})
        await client.login(login, pw)

        assert client.token is not None


@pytest.mark.asyncio
async def test_scores(authorized_client):
    with aioresponses() as m:
        m.get(url + "/scores", payload={"result": []})
        data = await authorized_client.get_scores()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_score(authorized_client):
    with aioresponses() as m:
        m.get(url + "/score", payload={"result": {"sadam": 36}})
        data = await authorized_client.get_score("sadam")
        assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_score_fail(authorized_client):
    with aioresponses() as m:
        m.get(url + "/score", payload={"result": "Invalid Name"})
        with pytest.raises(hscp.InvalidName):
            data = await authorized_client.get_score("your mom")


@pytest.mark.asyncio
async def test_score_uploader(authorized_client):
    loop = asyncio.get_event_loop_policy().new_event_loop()

    with aioresponses() as m:
        m.post(url + "/score", payload={"result": True})
        data = await authorized_client.post_score("sadam", 69)
        assert data is True


def test_logout(authorized_client):
    authorized_client.logout()
    assert authorized_client.token is None
