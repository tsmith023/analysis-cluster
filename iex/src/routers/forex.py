from collections import defaultdict
from datetime import date
from fastapi import Depends, APIRouter, HTTPException, Query
from pydantic import Required
from typing import List

from ..connections import Connections, connections_dep
from ..manager import IEXAPI
from .. import models, utils

router = APIRouter()


@router.get("/latest-forexes")
async def retrieve_the_latest_forex_rates_for_given_currencies(
    symbols: List[str] = Query(description="Provide the conversion symbols in the form `f'{from}{to}'`, e.g. USDGBP for USD into GBP. If the symbol is misspelled then a null is returned."),
    connections: Connections = Depends(connections_dep)
):
    iex_api = IEXAPI(connections.redis, connections.iex)
    try:
        result = await iex_api.get_latest_rates(symbols)
    except:
        raise HTTPException(status_code=500, detail="The server failed to process the request")

    return {datum.get('symbol'): models.ForexDatum.from_iex_response({
        **datum,
        "date": str(date.today())
    }) for datum in result}


@router.get("/historical-forexes")
async def retrieve_the_historical_forex_rates_for_given_currencies(
    period: models.Period = Query(default=Required),
    symbols: List[str] = Query(description="Provide the conversion symbols in the form `f'{from}{to}'`, e.g. USDGBP for USD into GBP. If the symbol is misspelled then a null is returned."),
    connections: Connections = Depends(connections_dep)
):
    iex_api = IEXAPI(connections.redis, connections.iex)
    start_date, end_date = utils.convert_period_into_datetime_period(period)
    try:
        result = await iex_api.get_historical_rates(end_date, start_date, symbols)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="The server failed to process the request, check your conversion symbol inputs")

    output = defaultdict(list)
    for symbol, data in result.items():
        for datum in data:
            if datum.get('date') is None: continue
            if datum.get('rate') is None: continue
            output[symbol].append(models.ForexDatum.from_iex_response(datum))

    return output