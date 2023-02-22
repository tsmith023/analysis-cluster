from fastapi import Depends, APIRouter, HTTPException, Query
from itertools import dropwhile
from pydantic import Required
from typing import List

from ..connections import Connections, connections_dep
from ..manager import IEXAPI
from .. import models, utils

router = APIRouter()


@router.get('/historical-prices')
async def retrieve_the_historical_prices_for_given_ticker_symbols(
    period: models.Period = Query(default=Required),
    symbols: List[str] = Query(default=Required),
    connections: Connections = Depends(connections_dep)
):
    iex_api = IEXAPI(connections.redis, connections.iex)
    try:
        result = await iex_api.get_historical_prices(utils.select_period(period), symbols)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="The server failed to process the request")
    start_date, _ = utils.convert_period_into_datetime_period(period)
    return {key: [models.TickerDatum.from_iex_response(datum) for datum in dropwhile(lambda t_d: utils.convert_date(t_d.get("date")) < start_date, value)] for key, value in result.items()}


@router.get('/latest-quotes')
async def retrieve_the_latest_quotes_for_given_ticker_symbols(
    symbols: List[str] = Query(default=Required),
    connections: Connections = Depends(connections_dep)
):  
    iex_api = IEXAPI(connections.redis, connections.iex)
    try:
        result = await iex_api.get_latest_quotes(symbols)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="The server failed to process the request")
    return {key: models.TickerQuote.from_iex_response(value) for key, value in result.items()}


@router.get('/latest-stats')
async def retrieve_the_latest_stats_for_given_ticker_symbols(
    symbols: List[str] = Query(default=Required),
    connections: Connections = Depends(connections_dep)
):
    iex_api = IEXAPI(connections.redis, connections.iex)
    try:
        result = await iex_api.get_latest_stats(symbols)
    except:
        raise HTTPException(status_code=500, detail="The server failed to process the request")
    return {stats.get('symbol'): models.TickerStats.from_iex_response(stats) for stats in result}
