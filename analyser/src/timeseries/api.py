import asyncio
import json
import nats
import os

from aioredis import Redis, from_url
from datetime import timedelta
from nats import connect
from typing import Any

from .. import models
from .utils import minutes_until_midnight

class TimeseriesAPI:
    '''
    This API functions as the principal calculator of the web-app.
    It takes a group of trades as an input and outputs historical timeseries data based on them in their native currencies.

    TODO: Implement a Redis caching layer to speed-up performance of this microservice
    '''
    _cache: Redis
    _nc: nats.NATS
    

    def __init__(self, cache: Redis, nc: nats.NATS):
        self._cache = cache
        self._nc = nc


    @classmethod
    async def create(cls) -> 'TimeseriesAPI':
        return cls(
            await from_url(
                os.environ.get("REDIS_URL"),
                encoding="utf-8",
                decode_responses=True,
            ),
            await connect(os.environ.get("NATS_URL")),
        )


    async def close(self):
        await self._cache.close()
        await self._nc.close()


    async def __retrieve_timeseries_result_from_cache(self, hash: str) -> dict:
        async with self._cache.pipeline() as pipe:
            await pipe.hgetall(hash)
            data = await pipe.execute()
        if data is None: return None
        out = data[0].get("result")
        return json.loads(out) if out is not None else None


    async def __set_timeseries_result_to_cache(self, hash: str, value: Any):
        async with self._cache.pipeline() as pipe:
            await pipe.hset(name=hash, key="result", value=json.dumps(value))
            ttl = minutes_until_midnight()
            if ttl > 0:
                await pipe.expire(hash, timedelta(minutes=ttl))
            await pipe.execute()


    def __create_hash(self, id: str, range: str) -> str:
        return f"timeseries:{id}:{range}"


    async def return_cached_results(self, id: str, range: str) -> dict | None:
        return await self.__retrieve_timeseries_result_from_cache(self.__create_hash(id, range))
            

    async def return_portfolio_timeseries_data(self, inputs: models.TimeseriesInputs) -> models.TimeseriesResult | None:
        cached_results = await self.return_cached_results(inputs.id, inputs.range)
        if cached_results is not None:
            try:
                return models.TimeseriesResult.parse_raw(cached_results)
            except Exception as e:
                print(cached_results)
                raise Exception(f"Error occured parsing cached_results to TimeseriesResult {e}")

        await self.publish_request(inputs)

        new_results = await self.return_cached_results(inputs.id, inputs.range)
        count = 0
        while (new_results is None or new_results == "null"):
            if count == 5:
                raise Exception("Server timed-out while waiting for a response from analysis-worker")
            await asyncio.sleep(1)
            new_results = await self.return_cached_results(inputs.id, inputs.range)
            count += 1
        
        try:
            return models.TimeseriesResult.parse_raw(new_results)
        except Exception as e:
            print(new_results)
            raise Exception(f"Error occured parsing new_results to TimeseriesResult {e}")



    async def publish_request(self, inputs: models.TimeseriesInputs):
        data = json.dumps(inputs.dict()).encode("UTF-8")
        await self._nc.publish(os.environ.get("TIMESERIES_PUBLICATION_TASK"), data)
        print(f"published timeseries request for user {inputs.id} over period {inputs.range}")


    async def write_results_to_cache(self, result: models.TimeseriesResult):
        await self.__set_timeseries_result_to_cache(self.__create_hash(result.id, result.range), result.json())