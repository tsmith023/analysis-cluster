import asyncio
from .api import TimeseriesAPI

class TimeseriesAPIDep:
    _lock: asyncio.Lock
    api: TimeseriesAPI | None

    def __init__(self):
        self.api = None
        self._lock = asyncio.Lock()

    async def __call__(self) -> 'TimeseriesAPI':
        if self.api:
            return self.api

        async with self._lock:
            if self.api:
                return self.api
            if self.api is None:
                self.api = await TimeseriesAPI.create()
                
        print("Initialised TimeseriesAPI")
        return self.api

    async def close(self):
        if self.api is not None:
            await self.api.close()

timeseries_api_dep = TimeseriesAPIDep()