# from collections import defaultdict
# from datetime import date
# from fastapi import Depends, APIRouter, HTTPException, Query
# from pydantic import Required
# from typing import List

# from ..manager import IEXAPI, yield_iex
# from .. import models, utils

# router = APIRouter()


# @router.get("/historical-prices-and-forexes")
# async def retrieve_the_historical_prices_for_given_ticker_symbols_with_their_forexes(
#     range: models.Range = Query(default=Required),
#     symbols: List[str] = Query(default=Required),
#     iex_api: IEXAPI = Depends(yield_iex)
# ):
#     start_date, end_date = utils.convert_range_into_datetime_period(range)
#     try:
#         prices_data = await iex_api.get_historical_prices(range, symbols)
#         rates_data = await iex_api.get_historical_rates(end_date, start_date, ['USDGBP', 'USDEUR'])
#     except:
#         raise HTTPException(status_code=500, detail="The server failed to process the request")

#     transformed_rates = defaultdict(dict)
#     for rates in rates_data:
#         for rate in rates:
#             print(rate)
#             if rate.get('rate') is None: continue
#             transformed_rates[rate.get('date')] = {
#                 **transformed_rates[rate.get('date')],
#                 rate.get('symbol'): rate.get("rate"),
#                 "USDUSD": 1,
#             }

#     output = defaultdict(list)
#     for symbol, value in prices_data.items():
#         for price in value.get('chart'):
#             forexes: dict = transformed_rates.get(price.get('date'))
#             if forexes is None: continue
#             output[symbol].append(models.TickerForexDatum.from_iex_response({
#                 **price,
#                 "forexes": transformed_rates.get(price.get('date'))
#             }))
#     return output