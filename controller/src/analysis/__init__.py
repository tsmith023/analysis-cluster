import asyncio
from .api import AnalysisAPI

class AnalysisAPIDep:
    _lock: asyncio.Lock
    api: AnalysisAPI | None

    def __init__(self):
        self.api = None
        self._lock = asyncio.Lock()

    async def __call__(self) -> 'AnalysisAPI':
        if self.api:
            return self.api

        async with self._lock:
            if self.api:
                return self.api
            if self.api is None:
                self.api = await AnalysisAPI.create()
                
        print("Initialised AnalysisAPI")
        return self.api

    async def close(self):
        if self.api is not None:
            await self.api.close()

analysis_api_dep = AnalysisAPIDep()