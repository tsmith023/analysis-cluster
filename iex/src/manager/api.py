import json
import os
from aiohttp import ClientSession
from aiometer import run_all
from aioredis import from_url, Redis
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from functools import partial
from typing import Any, Dict, List, Tuple, Union

from .. import utils

class IEXAPI:
    '''
    IEX Cloud provides free caching of requests: https://iexcloud.io/cloud-cache/
    so there is no need to configure a Redis cache with this manager.

    It therefore acts simply as a store off all queries used by the backend microservice stack.

    TODO: Implement a Redis caching layer to speed-up performance of this microservice
    '''
    _api_key: str
    _base_url: str
    _cache: Redis
    _session: ClientSession
    

    def __init__(self, cache: Redis, session: ClientSession):
        self._api_key = os.environ.get('IEX_CLOUD_API_KEY')
        self._base_url = os.environ.get('IEX_CLOUD_ENDPOINT')
        self._cache = cache
        self._session = session
    

    async def __retrieve_field_from_cache_by_hashes(self, hashes: List[str], key: str) -> Tuple[List[str], dict]:
        async with self._cache.pipeline() as pipe:
            for hash in hashes:
                await pipe.hget(hash, key)
            data = await pipe.execute()
        cached_data = {list(hashes)[i]: json.loads(data[i]) if data[i] is not None else None for i in range(0, len(hashes))}
        cache_misses = []
        for key, value in cached_data.items():
            if value is None: cache_misses.append(key)
        return cache_misses, cached_data



    async def __set_expiring_field_to_cache_by_hash_map(self, hash_map: Dict[str, Any], key: str, life_in_minutes: int):
        async with self._cache.pipeline() as pipe:
            for hash, value in hash_map.items():
                await pipe.hset(name=hash, key=key, value=json.dumps(value))
            if life_in_minutes > 0:
                await pipe.expire(hash, timedelta(minutes=life_in_minutes))
            await pipe.execute()

    def __calculate_moving_average(self, values: list[float], how_many: int) -> float:
        if len(values) > how_many:
            l = values[-how_many:]
            return sum(l) / len(l)
        else:
            return sum(values) / len(values)
    
    async def get_historical_rates(self, end_date: datetime, start_date: datetime, symbols: List[str]) -> Dict[str, List[dict]]:
        def create_missing_datum(date: datetime, moving_averages: dict[str, dict]) -> dict:
            return {
                "date": date.strftime("%Y-%m-%d"),
                "isDerived": False,
                "rate": moving_averages["day10MovingAverage"],
                "timestamp": date.timestamp(),
                **moving_averages
            }

        def fill_in_missing_dates(date: datetime, forexes_by_date: dict[str, dict], moving_averages: dict[str, float], previous_date: datetime):
            diff: timedelta = date - previous_date
            how_many_days_between = int(diff.total_seconds() / 86400)
            if how_many_days_between > 1:
                for day in range(how_many_days_between):
                    missing_date = previous_date + timedelta(days=day)
                    missing_date_str = missing_date.strftime("%Y-%m-%d")
                    forexes_by_date[missing_date_str] = create_missing_datum(missing_date, moving_averages)

        from_date = (start_date - relativedelta(days=1)).strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')

        cache_key = f"forex_data:{from_date}:{to_date}"
        cache_misses, cached_rates = await self.__retrieve_field_from_cache_by_hashes(symbols, cache_key)
        if len(cache_misses) == 0:
            return cached_rates
            # cache_misses = symbols

        url = f"{self._base_url}/fx/historical?sort=asc&symbols={','.join(cache_misses)}&from={from_date}&to={to_date}&token={self._api_key}"
        async with self._session.get(url) as response:
            data = await response.read()
            if response.status == 200:
                retrieved_prices: List[List[dict]] = json.loads(data)
            else:
                print(data)
                raise Exception('Failure in retrieving IEX historical forex rates for {}. {}'.format(symbols, data))


        forex_data_by_symbol = defaultdict(list)
        for forex_data in retrieved_prices:
            rates: list[float] = []
            forexes_by_date: dict[str, dict] = {}
            symbol: str | None = None

            previous_date: datetime = datetime.strptime(from_date, '%Y-%m-%d')
            for datum in forex_data:
                rate: float | None = datum.get("rate")
                if rate is not None:
                    rates.append(rate)

                moving_averages = {
                    "day10MovingAverage": self.__calculate_moving_average(rates, 10),
                    "day20MovingAverage": self.__calculate_moving_average(rates, 20),
                    "day50MovingAverage": self.__calculate_moving_average(rates, 50),
                    "day100MovingAverage": self.__calculate_moving_average(rates, 100),
                    "day200MovingAverage": self.__calculate_moving_average(rates, 200),
                }

                date_str = datum.get("date")
                date = datetime.strptime(date_str, "%Y-%m-%d")
                fill_in_missing_dates(date, forexes_by_date, moving_averages, previous_date)

                if symbol == None:
                    symbol = datum.get("symbol")

                if rate is None:
                    forexes_by_date[date_str] = {
                        **datum,
                        "rate": moving_averages["day10MovingAverage"],
                        **moving_averages
                    }
                else:
                    forexes_by_date[date_str] = {
                        **datum,
                        **moving_averages
                    }

                previous_date = date

            today = datetime.now()
            today_str = today.strftime("%Y-%m-%d")
            fill_in_missing_dates(today, forexes_by_date, moving_averages, previous_date)
            if forexes_by_date.get(today_str) is None:
                forexes_by_date[today_str] = create_missing_datum(today, moving_averages)
            forex_data_by_symbol[symbol] = list(forexes_by_date.values())

        await self.__set_expiring_field_to_cache_by_hash_map(forex_data_by_symbol, cache_key, utils.minutes_until_midnight())

        for key, value in forex_data_by_symbol.items():
            cached_rates[key] = value

        return cached_rates

    async def get_latest_rates(self, symbols: List[str]) -> List[dict]:

        url = f"{self._base_url}/fx/latest?symbols={','.join(symbols)}&token={self._api_key}"

        async with self._session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(response.text)
                raise Exception('Failure in retrieving IEX historical forex rates for {}. {}'.format(symbols, response.text))


    # async def get_latest_quotes(self, symbols: List[str]) -> Dict[str, dict]:
    #     cache_results = await self.__retrieve_field_from_cache_by_hashes(symbols, 'quote')

    #     cached_quotes, missed_keys = {}, []
    #     for key, value in cache_results.items():
    #         if value is not None: cached_quotes[key] = value
    #         if value is None: missed_keys.append(key)

    #     url = f"/stock/market/batch?types=quote&symbols={','.join(missed_keys)}&token={self._api_key}"

    #     if missed_keys:
    #         async with self._session.get(url) as response:
    #             if response.status == 200:
    #                 retrieved = await response.json()
    #             else:
    #                 print(response.text)
    #                 raise Exception('Failure in retrieving IEX latest quotes for {}. {}'.format(symbols, response.text))
    #         quotes = {**cached_quotes, **retrieved}
    #         await self.__set_expiring_field_to_cache_by_hash_map(quotes, 'quote', minutes_until_quarter())
    #     else:
    #         quotes = cached_quotes
    #     return quotes

    async def get_latest_quotes(self, symbols: set) -> Dict[str, Dict[str, dict]]:

        url = f"{self._base_url}/stock/market/batch?types=quote&symbols={','.join(symbols)}&token={self._api_key}"

        async with self._session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(response.text)
                raise Exception('Failure in retrieving IEX latest quotes for {}. {}'.format(symbols, response.text))
        

    async def get_latest_stats(self, symbols: List[str]) -> List[dict]:
        async def send_request(symbol: str):

            url = f"{self._base_url}/stock/{symbol}/stats?token={self._api_key}"

            async with self._session.get(url) as response:
                try:
                    data = await response.json()
                    data['symbol'] = symbol
                    return data
                except:
                    print(response.text)
                    raise Exception('Failure in retrieving IEX latest stats for {}. {}'.format(symbol, response.text))
                
        jobs = [partial(send_request, symbol) for symbol in symbols]
        return await run_all(jobs, max_per_second=50)


    async def get_historical_prices(self, period: str, symbols: List[str]) -> Dict[str, List[dict]]:
        def calculate_moving_averages(closes: List[float]) -> Dict[str, float]:
            if len(closes) >= 20:
                twenty_days = closes[-20:]
                twenty_day = round(sum(twenty_days) / len(twenty_days), 2)
            else:
                twenty_day = None
            if len(closes) >= 50:
                fifty_days = closes[-50:]
                fifty_day = round(sum(fifty_days) / len(fifty_days), 2)
            else:
                fifty_day = None
            if len(closes) >= 100:
                one_hundred_days = closes[-100:]
                one_hundred_day = round(sum(one_hundred_days) / len(one_hundred_days), 2)
            else:
                one_hundred_day = None
            if len(closes) >= 200:
                two_hundred_days = closes[-200:]
                two_hundred_day = round(sum(two_hundred_days) / len(two_hundred_days), 2)
            else:
                two_hundred_day = None
            return {
                "day20MovingAverage": twenty_day,
                "day50MovingAverage": fifty_day,
                "day100MovingAverage": one_hundred_day,
                "day200MovingAverage": two_hundred_day
            }

        def transform_prices_to_include_moving_averages(data: List[dict]) -> List[dict]:
            closes: List[float] = []
            new_data: List[dict] = []
            for datum in data:
                closes.append(datum.get("close"))
                moving_averages = calculate_moving_averages(closes)
                new_data.append({**datum, **moving_averages})
            return new_data
        
        # overfetch the period and then filter result accordingly afterwards
        # in this way, we can calculate the moving averages and cache them
        if period in ["6m", "ytd", "1y"]:
            period = "2y"
        elif period == "2y":
            period = "5y"
        elif period == "5y":
            period = "5y"
        else:
            period = "max"

        cache_key = f"ticker_data:{period}"
        cache_misses, cached_prices = await self.__retrieve_field_from_cache_by_hashes(symbols, cache_key)
        # if len(cache_misses) == 0:
        #     return cached_prices

        url = f"{self._base_url}/stock/market/batch?chartCloseOnly=true&sort=asc&includeToday=true&symbols={','.join(symbols)}&types=chart&range={period}&token={self._api_key}"

        async with self._session.get(url) as response:
            data = await response.read()
            if response.status == 200:
                retrieved_prices: Dict[str, Dict[str, List[dict]]] = json.loads(data)
            else:
                print(data)
                raise Exception('IEX_STORES: Failure in retrieving IEX historical ticker price data. {}'.format(response.text))

        modified_prices = {
            key: transform_prices_to_include_moving_averages(value.get("chart"))
        for key, value in retrieved_prices.items()}

        await self.__set_expiring_field_to_cache_by_hash_map(modified_prices, cache_key, utils.minutes_until_midnight())

        for key, value in modified_prices.items():
            cached_prices[key] = value

        return cached_prices