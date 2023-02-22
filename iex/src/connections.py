import asyncio
import os
from aiohttp import ClientSession
from aioredis import from_url, Redis

class Connections:
    iex: ClientSession | None
    redis: Redis | None

    def __init__(self):
        self._lock = asyncio.Lock()
        self.iex = None
        self.redis = None

    async def __call__(self) -> 'Connections':
        if self.iex and self.redis:
            return self

        async with self._lock:
            if self.iex and self.redis:
                return self
            if self.iex is None:
                self.iex = ClientSession()
            if self.redis is None:
                self.redis = await from_url(
                    os.environ.get("REDIS_URL"),
                    encoding="utf-8",
                    decode_responses=True,
                )
        
        return self

    async def connect_iex(self):
        self.iex = await ClientSession()
        self.redis = await from_url(
            os.environ.get("REDIS_URI"),
            encoding="utf-8",
            decode_responses=True,
        )

    async def close(self):
        if self.iex is not None:
            await self.iex.close()
        if self.redis is not None:
            await self.redis.close()

connections_dep = Connections()