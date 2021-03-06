from typing import Any, Awaitable, Callable, Coroutine, Literal, TypedDict, Union

import aiohttp
from multidict import CIMultiDictProxy
from yarl import URL


class Dispatch(TypedDict):
    json: Callable[[], Awaitable[Any]]
    read: Callable[[], Awaitable[bytes]]
    text: Callable[[], Awaitable[str]]


class Response:
    def __init__(
        self,
        status: int,
        message: str,
        body: Any,
        url: URL,
        headers: CIMultiDictProxy[str],
    ):
        self.status = status
        self.message = message
        self.body = body
        self.url = url
        self.headers = headers


class Request:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @property
    def headers(self):
        return self.kwargs.get("headers")

    async def fetch(
        self,
        session: aiohttp.ClientSession,
        url: str,
        method: str,
        response_method: Literal["json", "read", "text"],
        *args,
        **kwargs,
    ) -> Response:
        async with session.request(method, url, *args, **kwargs) as response:
            dispatch: Dispatch = {
                "json": response.json,
                "read": response.read,
                "text": response.text,
            }
            if response_method not in dispatch:
                raise ValueError(f"Invalid response_method value: {response_method}")
            return Response(
                response.status,
                response.reason,
                await dispatch[response_method](),
                response.url,
                response.headers,
            )

    async def request(
        self,
        url: str,
        method: str,
        response_method: Literal["json", "read", "text"],
        *args,
        **kwargs,
    ) -> Response:
        async with aiohttp.ClientSession(*self.args, **self.kwargs) as session:
            response = await self.fetch(
                session, url, method, response_method, *args, **kwargs
            )
            return response

    async def get(
        self,
        url: str,
        response_method: Literal["json", "read", "text"] = "read",
        *args,
        **kwargs,
    ) -> Response:
        """Perform HTTP GET request."""
        return await self.request(url, "GET", response_method, *args, **kwargs)

    async def post(
        self,
        url: str,
        response_method: Literal["json", "read", "text"],
        *args,
        **kwargs,
    ) -> Response:
        """Perform HTTP POST request."""
        return await self.request(url, "POST", response_method, *args, **kwargs)


request = Request()
