import json
import os

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from itertools import dropwhile
from redis import Redis
from requests import Session
from typing import Any, Dict, List, Tuple

from .. import models
from .utils import minutes_until_quarter, minutes_until_midnight

class PortfolioAPI:
    '''
    This API functions as the principal calculator of the web-app.
    It takes a group of trades as an input and outputs historical timeseries data based on them in their native currencies.

    TODO: Implement a Redis caching layer to speed-up performance of this microservice
    '''
    _cache: Redis
    _session: Session
    

    @classmethod
    def create(cls):
        self = PortfolioAPI()
        # self._cache = Redis(
        #     host=os.environ.get('REDIS_HOST'),
        #     port=int(os.environ.get('REDIS_PORT')),
        #     encoding="utf-8",
        #     decode_responses=True,
        # )
        self._session = self.__return_session()
        return self


    def close(self):
        self._session.close()
    

    def __return_session(self):
        session = Session()
        session.headers.update({"Authorization": os.environ.get('IEX_CLOUD_API_KEY')})
        return session


    def __make_request(self, path: str) -> Dict[str, dict]:
        base_url = f"http://{os.environ.get('IEX_HOST')}:{os.environ.get('IEX_PORT')}"
        response = self._session.get(f"{base_url}{path}")
        data: dict = response.json()
        if response.status_code == 200:
            return data
        else:
            print(data)
            return {}


    async def __retrieve_field_from_cache_by_hashes(self, hashes: List[str], key: str) -> Dict[str, str]:
        async with self._cache.pipeline() as pipe:
            for hash in hashes:
                await pipe.hget(hash, key)
            data = await pipe.execute()
        return {list(hashes)[i]: json.loads(data[i]) if data[i] is not None else None for i in range(0,len(hashes))}


    async def __set_expiring_field_to_cache_by_hash_map(self, hash_map: Dict[str, Any], key: str, life_in_minutes: int):
        async with self._cache.pipeline() as pipe:
            for hash, value in hash_map.items():
                await pipe.hset(name = hash, key = key, value = json.dumps(value))
            if life_in_minutes > 0:
                await pipe.expire(hash, timedelta(minutes = life_in_minutes))
            await pipe.execute()


    def __convert_date(self, date: str) -> datetime:
        if date is None: return None
        return datetime.strptime(date, "%Y-%m-%d")


    def __get_historical_prices(self, range: models.Range, symbols: List[str]) -> Dict[str, List[models.TickerDatum]]:
        query_string = '&symbols='.join(symbols)
        data: Dict[str, List[dict]] = self.__make_request(f'/historical-prices-and-forexes?range={range}&symbols={query_string}')
        return {
            key: [
                models.TickerDatum(
                    change=datum.get('change'),
                    change_over_time=datum.get('change_over_time'),
                    change_percent=datum.get('change_percent'),
                    close=datum.get('close'),
                    date=datum.get('date'),
                    to_eur=datum.get('to_eur'),
                    to_gbp=datum.get('to_gbp'),
                    to_usd=datum.get('to_usd'),
                    volume=datum.get('volume'),
                ) for datum in value
            ] for key, value in data.items()
        }


    def __calculate_cumulative_data(self, first_ticker_datum_date: datetime, trades: List[models.Trade]) -> Tuple[Decimal, Decimal, Dict[str, List[models.Trade]]]:
        cumulative_cost, cumulative_shares, trades_by_date = Decimal("0.0"), Decimal("0.0"), defaultdict(list)
        for trade in trades:
            trades_by_date[trade.date].append(trade)
            if self.__convert_date(trade.date) < first_ticker_datum_date:
                if trade.buy_or_sell:
                    sign = +1
                else:
                    sign = -1
                cumulative_cost += sign * trade.cost
                cumulative_shares += sign * trade.shares
        return cumulative_cost, cumulative_shares, trades_by_date


    def __calculate_holding_data(self, ticker_data: List[models.TickerDatum], trades: List[models.Trade]) -> List[models.HoldingDatum]:
        holding_data: List[models.HoldingDatum] = []
        trades.sort(key=lambda trade: self.__convert_date(trade.date))
        first_ticker_datum_date = self.__convert_date(ticker_data[0].date)
        first_trade_date = self.__convert_date(trades[0].date)

        cumulative_cost, cumulative_shares, trades_by_date = self.__calculate_cumulative_data(first_ticker_datum_date, trades)
        for ticker_datum in dropwhile(lambda t_d: self.__convert_date(t_d.date) < first_trade_date, ticker_data):
            date = ticker_datum.date
            trades: List[models.Trade] = trades_by_date.get(date)
            if trades is not None:
                for trade in trades:
                    if trade.buy_or_sell:
                        sign = +1
                    else:
                        sign = -1
                    cumulative_cost += sign * trade.cost
                    cumulative_shares += sign * trade.shares

            if True:
                # TODO: write logic to choose correct forex for given currency
                forex = ticker_datum.to_gbp

            if forex is None:
                # can happen if errors in IEX call to forex data
                continue

            holding_data.append(models.HoldingDatum(
                cost=cumulative_cost,
                date=date,
                shares=cumulative_shares,
                value=cumulative_shares * ticker_datum.close * forex
            ))
        return holding_data


    def __calculate_holdings_data(self, holdings: List[models.Holding], ticker_data_by_symbol: Dict[str, List[dict]]) -> Dict[str, List[dict]]:
        holding_data_by_symbol = {}
        for holding in holdings:
            holding_data_by_symbol[holding.symbol] = self.__calculate_holding_data(
                ticker_data_by_symbol[holding.symbol],
                holding.trades
            )
        return holding_data_by_symbol


    def __calculate_portfolio_data(self, holding_data_by_symbol: Dict[str, List[models.HoldingDatum]]) -> Dict[str, float]:
        portfolio_value_by_date = defaultdict(Decimal)
        for symbol, holding_data in holding_data_by_symbol.items():
            for datum in holding_data:
                portfolio_value_by_date[datum.date] += datum.value
        return portfolio_value_by_date


    def calculate_portfolio_timeseries_data(self, holdings: List[models.Holding], range: models.Range) -> List[models.PortfolioDatum]:
        ticker_data_by_symbol = self.__get_historical_prices(range, [holding.symbol for holding in holdings])
        holding_data_by_symbol = self.__calculate_holdings_data(holdings, ticker_data_by_symbol)
        portfolio_value_by_date = self.__calculate_portfolio_data(holding_data_by_symbol)
        data = [models.PortfolioDatum(
            date=key,
            value=value
        ) for key, value in portfolio_value_by_date.items()]
        data.sort(key=lambda d: d.date)
        return data




        



    # async def calculate_portfolio_data(cache: Redis, local_currency: str, info: Info, range: str, trades: List[dict]) -> List[Dict]:
    #     expiry_time = minutes_until_midnight()
    #     currency_pairs, tickers = set(), set()
    #     cumulative_shares_by_ticker: Dict[str, float] = defaultdict(float)
    #     trades_by_date: Dict[str, List[PortfolioTrade]] = defaultdict(list)
    #     for trade in trades:
    #         ticker: Ticker = await info.context['dataloaders']['ticker_by_trade'].load(trade.id)
    #         trade.currency_symbol = ticker.currency
    #         trade.ticker_symbol = ticker.symbol
    #         if trade.currency_symbol not in currency_pairs and trade.currency_symbol is not local_currency:
    #             pair = trade.currency_symbol + local_currency
    #             currency_pairs.add(pair)
    #         if trade.ticker_symbol not in tickers:
    #             tickers.add(ticker.symbol)
    #         trades_by_date[trade.date].append(trade)

    #     forex_hashes = {'forex:{}'.format(currency_pair) for currency_pair in currency_pairs}
    #     ticker_hashes = {'ticker:{}'.format(ticker) for ticker in tickers}

    #     cached_forex_data = await retrieve_field_from_cache_by_hashes(cache, forex_hashes, 'data')
    #     cached_ticker_data = await retrieve_field_from_cache_by_hashes(cache, ticker_hashes, 'data_{}'.format(range))
        
    #     remove = set()
    #     for key, value in cached_ticker_data.items():
    #         if value is not None:
    #             tickers.remove(key)
    #         else:
    #             remove.add(key)
    #     for key in remove: del cached_ticker_data[key]

    #     remove = set()
    #     for key, value in cached_forex_data.items():
    #         if value is not None:
    #             currency_pairs.remove(key)
    #         else:
    #             remove.add(key)
    #     for key in remove: del cached_forex_data[key]

    #     fetched_forex_data, fetched_ticker_data = {}, {}
    #     if len(currency_pairs) > 0 or len(tickers) > 0:
    #         try:
    #             fetched_forex_data, fetched_ticker_data = await iex_methods.get_historical_ticker_prices_and_forexes(currency_pairs, range, info.context['session'], tickers)
    #         except Exception as e:
    #             print("Exception occured in users.resolvers.calculate_portfolio_data", e)
    #             return []

    #     prices_by_hash = {**cached_ticker_data, **fetched_ticker_data}
    #     forexes_by_hash = {**cached_forex_data, **fetched_forex_data}

    #     dates = set()
    #     prices_forexes_and_dates_by_symbol = {}
    #     rates = []
    #     for hash, prices in prices_by_hash.items():
    #         closes_by_date = {}
    #         for datum in prices:
    #             if datum.get('close') is None: continue
    #             closes_by_date[datum['date']] = datum['close']
    #             dates.add(datum['date'])
    #         prices_forexes_and_dates_by_symbol[hash.split(':')[1]] = closes_by_date
    #     prices_forexes_and_dates_by_symbol['dates'] = sorted(dates)

    #     for hash, forex_data in forexes_by_hash.items():
    #         currency_pair = hash.split(':')[1]
    #         if currency_pair not in prices_forexes_and_dates_by_symbol.keys():
    #             prices_forexes_and_dates_by_symbol[currency_pair] = {}
    #         for forex_datum in forex_data:
    #             if forex_datum.get('rate') is None: continue
    #             date = forex_datum['date']
    #             rate = forex_datum['rate']
    #             prices_forexes_and_dates_by_symbol[currency_pair][date] = rate
    #             rates.append(rate)
    #         latest_250_rates = rates[:250]
    #         if len(latest_250_rates) > 0:
    #             prices_forexes_and_dates_by_symbol[currency_pair]['average'] = sum(latest_250_rates) / len(latest_250_rates) # 250 day moving average
    #         else:
    #             prices_forexes_and_dates_by_symbol[currency_pair]['average'] = 0

    #     start_date = prices_forexes_and_dates_by_symbol['dates'][0]

    #     count = 0
    #     trades_dates = sorted(trades_by_date.keys())
    #     while count < len(trades_dates) and trades_dates[count] < start_date:
    #         for trade in trades_by_date[trades_dates[count]]:
    #             if parse(trade.date).date() < parse(start_date).date():
    #                 if trade.buy_or_sell:
    #                     cumulative_shares_by_ticker['{}:{}{}'.format(trade.ticker_symbol, trade.currency_symbol, local_currency)] += float(trade.shares)
    #                 elif not trade.buy_or_sell:
    #                     cumulative_shares_by_ticker['{}:{}{}'.format(trade.ticker_symbol, trade.currency_symbol, local_currency)] -= float(trade.shares)
    #                 else:
    #                     print("Error in calculating cumulative shares for trade vertex {}".format(trade.id))
    #                     return None
    #         count += 1
        
    #     if count == 0: # i.e. start_date < first_trade_date
    #         dates = dropwhile(lambda d: d < trades_dates[count], prices_forexes_and_dates_by_symbol['dates'])
    #     else:
    #         dates = prices_forexes_and_dates_by_symbol['dates']

    #     portfolio_data = []
    #     for date in dates:
    #         for trade in trades_by_date[date]: # defaultdict yields empty list if date isn't a key
    #             if trade.buy_or_sell:
    #                 cumulative_shares_by_ticker['{}:{}{}'.format(trade.ticker_symbol, trade.currency_symbol, local_currency)] += float(trade.shares)
    #             elif not trade.buy_or_sell:
    #                 cumulative_shares_by_ticker['{}:{}{}'.format(trade.ticker_symbol, trade.currency_symbol, local_currency)] -= float(trade.shares)
    #             else:
    #                 print("Error in calculating cumulative shares for trade vertex {}".format(trade.id))
    #                 return None
    #         portfolio_value = 0
    #         for key, value in cumulative_shares_by_ticker.items():
    #             try:
    #                 ticker, currency_pair = key.split(':')
    #                 price = prices_forexes_and_dates_by_symbol[ticker][date]
    #                 forex = prices_forexes_and_dates_by_symbol[currency_pair][date] if prices_forexes_and_dates_by_symbol[currency_pair].get(date) is not None else prices_forexes_and_dates_by_symbol[currency_pair]['average']
    #             except Exception as e:
    #                 print(e, key, value)
    #                 return []
    #             portfolio_value += value * price * forex
    #         portfolio_data.append({
    #             'date': date,
    #             'value': portfolio_value,
    #         })
    #     return portfolio_data

    # async def calculate_portfolio_value(local_currency: str, session: ClientSession, trades: List[PortfolioTrade]):
    #     holding_data_by_ticker: Dict[str, Dict[str, float]] = {}
    #     portfolio_value: float = None
    #     if trades is not None:
    #         currency_by_ticker, cost_by_ticker, shares_by_ticker = {}, defaultdict(float), defaultdict(float)
    #         currencies, tickers = set(), set()
    #         portfolio_value = 0
    #         for trade in trades:
    #             if not trade.currency_symbol in currency_by_ticker:
    #                 currency_by_ticker[trade.ticker_symbol] = trade.currency_symbol

    #             currencies.add(trade.currency_symbol)
    #             tickers.add(trade.ticker_symbol)

    #             if trade.buy_or_sell:
    #                 cost_by_ticker[trade.ticker_symbol] += float(trade.cost)
    #                 shares_by_ticker[trade.ticker_symbol] += float(trade.shares)
    #             else:
    #                 cost_by_ticker[trade.ticker_symbol] -= float(trade.cost)
    #                 shares_by_ticker[trade.ticker_symbol] -= float(trade.shares)

    #         currency_pairs = {currency + local_currency for currency in currencies}
            
    #         tickers_and_forexes_by_symbol = await iex_methods.get_latest_ticker_data_and_forexes(currency_pairs, session, tickers)
    #         if tickers_and_forexes_by_symbol:
    #             for ticker, shares in shares_by_ticker.items():
    #                 forex: float = tickers_and_forexes_by_symbol[currency_by_ticker[ticker]]
    #                 quote: dict = tickers_and_forexes_by_symbol[ticker]['quote']
    #                 stats: dict = tickers_and_forexes_by_symbol[ticker]['stats']

    #                 holding_value = shares * forex * quote.get('latestPrice')
    #                 holding_data_by_ticker[ticker] = {
    #                     "change_percent": quote.get('changePercent'),
    #                     "change_value": shares * forex * quote.get('change'),
    #                     "cost": cost_by_ticker[ticker],
    #                     "fifty_day": shares * forex * stats.get('day50MovingAvg'),
    #                     "shares": shares,
    #                     "two_hundred_day": shares * forex * stats.get('day200MovingAvg'),
    #                     "value": holding_value
    #                 }
    #                 portfolio_value += holding_value
    #         else:
    #             raise Exception("Failed to retrieve latest data from IEX cloud")
    #     return portfolio_value, holding_data_by_ticker