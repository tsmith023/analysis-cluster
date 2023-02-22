import asyncio
import json
import nats
import os

from motor.motor_asyncio import AsyncIOMotorClient
from nats import connect

from .. import models

class AnalysisAPI:
    '''
    This API functions as the principal calculator of the web-app.
    It takes a group of trades as an input and outputs historical timeseries data based on them in their native currencies.

    TODO: Implement a Redis caching layer to speed-up performance of this microservice
    '''

    _client: AsyncIOMotorClient
    _nc: nats.NATS

    def __init__(self, client: AsyncIOMotorClient, nc: nats.NATS):
        self._client = client
        self._nc = nc


    @classmethod
    async def create(cls) -> 'AnalysisAPI':
        client = AsyncIOMotorClient(os.environ.get("MONGODB_URL"))
        print(await client.admin.command({ "ping": 1 }))
        return cls(
            client,
            await connect(os.environ.get("NATS_URL")),
        )

    async def close(self):
        await self._nc.close()


    async def __publish_request(self, inputs: models.PerformAnalysisInputs):
        data = json.dumps(inputs.dict()).encode("UTF-8")
        await self._nc.publish(os.environ.get("ANALYSIS_PUBLICATION_TASK"), data)
        print(f"published analysis request for user {inputs.id} and {inputs.range}")

    async def __retrieve_analysis_result(self, id: str, range: str) -> dict | None:
        collection = self._client[os.environ.get('STOX_DATABASE')][os.environ.get('ANALYSIS_COLLECTION')]
        return await collection.find_one({
            "id": { "$eq": id },
            "range": { "$eq": range },
        }, { "_id": False })


    async def __return_cached_results(self, id: str, range: str) -> dict | None:
        return await self.__retrieve_analysis_result(id, range)


    async def __set_analysis_result(self, data: list[dict]):
        collection = self._client[os.environ.get('STOX_DATABASE')][os.environ.get('ANALYSIS_COLLECTION')]
        await collection.insert_one(data)

    
    # async def return_portfolio_analysis_data(self, inputs: models.AnalysisInputs) -> models.AnalysisResult | None:
    #     cached_results = await self.__return_cached_results(inputs.id, inputs.range)
    #     if cached_results is not None:
    #         try:
    #             return models.AnalysisResult.parse_obj(cached_results)
    #         except Exception as e:
    #             print(cached_results)
    #             raise Exception(f"Error occured parsing cached_results to AnalysisResult {e}")

    #     await self.__publish_request(inputs)

    #     new_results = await self.__return_cached_results(inputs.id, inputs.range)
    #     count = 0
    #     while (new_results is None or new_results == "null"):
    #         if count == 5:
    #             raise Exception("Server timed-out while waiting for a response from analysis-worker")
    #         await asyncio.sleep(1)
    #         new_results = await self.__return_cached_results(inputs.id, inputs.range)
    #         count += 1
        
    #     try:
    #         return models.AnalysisResult.parse_obj(new_results)
    #     except Exception as e:
    #         print(new_results)
    #         raise Exception(f"Error occured parsing new_results to AnalysisResult {e}")

    async def return_portfolio_analysis(self, inputs: models.GetAnalysisInputs) -> models.AnalysisResult | None:
        cached_results = await self.__return_cached_results(inputs.id, inputs.range)
        if cached_results is not None:
            try:
                return models.AnalysisResult.parse_obj(cached_results)
            except Exception as e:
                print(cached_results)
                raise Exception(f"Error occured parsing cached_results to AnalysisResult {e}")
        else:
            return None

    async def perform_portfolio_analysis(self, inputs: models.PerformAnalysisInputs):
        try:
            await self.__publish_request(inputs)
        except Exception as e:
            print(e)
            raise Exception(f"Error occured when publishing request to {os.environ.get('ANALYSIS_PUBLICATION_QUEUE')}: {e}")


    async def write_results_to_mongo(self, result: models.AnalysisResult):
        await self.__set_analysis_result(result.dict())


    