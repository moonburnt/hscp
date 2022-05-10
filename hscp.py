import logging

from typing import Optional
from urllib.parse import urljoin as join

import aiohttp
import requests

log = logging.getLogger(__name__)


class AuthError(Exception):
    """Exception to raise when authentification has failed."""

    pass


class InvalidName(Exception):
    """Exception to raise when nickname can't be found."""

    pass


class TokenUnavailable(Exception):
    """Exception to raise when token isn't set."""

    pass


class _HSClientBase:
    def __init__(self, url, app: str, timeout: int = 30):
        self.url = url
        self.timeout = max(timeout, 0)
        self.app = app

        self._token = None

    @property
    def token(self):
        return self._token

    def require_token(func: callable):
        def inner(self, *args, **kwargs):
            if not self.token:
                raise TokenUnavailable

            return func(self, *args, **kwargs)

        return inner

    @require_token
    def logout(self):
        self.token = None


class HyScoresClient(_HSClientBase):
    def __init__(
        self, url, app: str, timeout: int = 30, user_agent: Optional[str] = None
    ):
        super().__init__(
            url=url,
            app=app,
            timeout=timeout,
        )

        self.session = requests.Session()

        if user_agent:
            self.session.headers["user-agent"] = user_agent

    @_HSClientBase.token.setter
    def token(self, val: str):
        self._token = val
        self.session.headers.update({"x-access-tokens": self._token})

    def register(self, username: str, password: str) -> bool:
        return (
            self.session.post(
                join(self.url, "register"),
                timeout=self.timeout,
                auth=(username, password),
                json={"app": self.app},
            )
            .json()
            .get("result", False)
        )

    def login(self, username: str, password: str):
        result = (
            self.session.post(
                join(self.url, "login"),
                timeout=self.timeout,
                auth=(username, password),
                json={"app": self.app},
            )
            .json()
            .get("result", None)
        )
        if result:
            token = result.get("token", None)
            if token:
                self.token = token
                return

        raise AuthError

    @_HSClientBase.require_token
    def get_scores(self) -> list:
        return self.session.get(
            join(self.url, "scores"),
            timeout=self.timeout,
            json={"app": self.app},
        ).json()["result"]

    @_HSClientBase.require_token
    def get_score(self, nickname: str) -> dict:
        result = self.session.get(
            join(self.url, "score"),
            timeout=self.timeout,
            json={
                "app": self.app,
                "nickname": nickname,
            },
        ).json()["result"]
        if type(result) is dict:
            return result
        else:
            raise InvalidName

    @_HSClientBase.require_token
    def post_score(self, nickname: str, score: int) -> bool:
        return self.session.post(
            join(self.url, "score"),
            timeout=self.timeout,
            json={
                "app": self.app,
                "nickname": nickname,
                "score": score,
            },
        ).json()["result"]


class HyScoresAsyncClient(_HSClientBase):
    def __init__(
        self, url, app: str, timeout: int = 30, user_agent: Optional[str] = None
    ):
        super().__init__(
            url=url,
            app=app,
            timeout=timeout,
        )

        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
        )

        if user_agent:
            self.session.headers["user-agent"] = user_agent

    @_HSClientBase.token.setter
    def token(self, val: str):
        self._token = val
        self.session.headers.update({"x-access-tokens": self._token})

    async def register(self, username: str, password: str) -> bool:
        async with self.session.post(
            join(self.url, "register"),
            timeout=self.timeout,
            auth=(username, password),
            json={"app": self.app},
        ) as response:
            data = await response.json()
            return data.get("result", False)

    async def login(self, username: str, password: str):
        async with self.session.post(
            join(self.url, "login"),
            timeout=self.timeout,
            auth=(username, password),
            json={"app": self.app},
        ) as response:
            data = await response.json()
            result = data.get("result", None)

            if result:
                token = result.get("token", None)
                if token:
                    self.token = token
                    return

        raise AuthError

    @_HSClientBase.require_token
    async def get_scores(self) -> list:
        async with self.session.get(
            join(self.url, "scores"),
            timeout=self.timeout,
            json={"app": self.app},
        ) as response:
            data = await response.json()
            return data["result"]

    @_HSClientBase.require_token
    async def get_score(self, nickname: str) -> dict:
        async with self.session.get(
            join(self.url, "score"),
            timeout=self.timeout,
            json={
                "app": self.app,
                "nickname": nickname,
            },
        ) as response:
            data = await response.json()
            result = data["result"]
            if type(result) is dict:
                return result
            else:
                raise InvalidName

    @_HSClientBase.require_token
    async def post_score(self, nickname: str, score: int) -> bool:
        async with self.session.post(
            join(self.url, "score"),
            timeout=self.timeout,
            json={
                "app": self.app,
                "nickname": nickname,
                "score": score,
            },
        ) as response:
            data = await response.json()
            return data["result"]
