from ... import models


def test_forex_datum():
    iex_data = {
        "date": "2021-12-05",
        "isDerived": False,
        "rate": 0.755538094230711,
        "timestamp": 1638748799216
    }
    forex_datum = models.ForexDatum.from_iex_response(iex_data)
    assert forex_datum.date == iex_data.get("date")
    assert forex_datum.is_derived == iex_data.get("isDerived")
    assert str(forex_datum.rate) == str(iex_data.get("rate"))
    assert str(forex_datum.timestamp) == str(iex_data.get("timestamp"))


def test_ticker_datum():
    iex_data = {
        "change": -47.83999999999992,
        "changeOverTime": -0.041352961006854635,
        "changePercent": -0.0414,
        "close": 1109.03,
        "date": "2021-11-23",
        "day50MovingAverage": 800,
        "day100MovingAverage": 900,
        "day200MovingAverage": 1000,
        "day20MovingAverage": 1100,
        "volume": 36171700
    }
    ticker_datum = models.TickerDatum.from_iex_response(iex_data)
    assert str(ticker_datum.change) == str(iex_data.get("change"))
    assert str(ticker_datum.change_over_time) == str(iex_data.get("changeOverTime"))
    assert str(ticker_datum.change_percent) == str(iex_data.get("changePercent"))
    assert str(ticker_datum.close) == str(iex_data.get("close"))
    assert str(ticker_datum.date) == str(iex_data.get("date"))
    assert str(ticker_datum.fifty_day) == str(iex_data.get("day50MovingAverage"))
    assert str(ticker_datum.one_hundred_day) == str(iex_data.get("day100MovingAverage"))
    assert str(ticker_datum.two_hundred_day) == str(iex_data.get("day200MovingAverage"))
    assert str(ticker_datum.twenty_day) == str(iex_data.get("day20MovingAverage"))
    assert str(ticker_datum.volume) == str(iex_data.get("volume"))


def test_ticker_forex_datum():
    iex_data = {
        "change": -47.83999999999992,
        "changeOverTime": -0.041352961006854635,
        "changePercent": -0.0414,
        "close": 1109.03,
        "date": "2021-11-23",
        "volume": 36171700,
        "forexes": {
            "USDGBP": 0.75,
            "USDEUR": 0.7,
            "USDUSD": 1
        }
    }
    ticker_datum = models.TickerForexDatum.from_iex_response(iex_data)
    assert str(ticker_datum.change) == str(iex_data.get("change"))
    assert str(ticker_datum.change_over_time) == str(iex_data.get("changeOverTime"))
    assert str(ticker_datum.change_percent) == str(iex_data.get("changePercent"))
    assert str(ticker_datum.close) == str(iex_data.get("close"))
    assert str(ticker_datum.date) == str(iex_data.get("date"))
    assert str(ticker_datum.to_gbp) == str(iex_data.get("forexes").get("USDGBP"))
    assert str(ticker_datum.to_eur) == str(iex_data.get("forexes").get("USDEUR"))
    assert str(ticker_datum.to_usd) == str(iex_data.get("forexes").get("USDUSD"))
    assert str(ticker_datum.volume) == str(iex_data.get("volume"))


def test_ticker_quote():
    iex_data = {
        "quote": {
            "symbol": "BAC",
            "companyName": "Bank Of America Corp.",
            "primaryExchange": "NEW YORK STOCK EXCHANGE, INC.",
            "calculationPrice": "close",
            "open": 28.81,
            "openTime": 1607437801023,
            "openSource": "official",
            "close": 28.81,
            "closeTime": 1607461201852,
            "closeSource": "official",
            "high": 29.12,
            "highTime": 1607461198592,
            "highSource": "15 minute delayed price",
            "low": 27.68,
            "lowTime": 1607437803011,
            "lowSource": "15 minute delayed price",
            "latestPrice": 28.81,
            "latestSource": "Close",
            "latestTime": "December 8, 2020",
            "latestUpdate": 1607461201852,
            "latestVolume": 33820759,
            "iexRealtimePrice": 28.815,
            "iexRealtimeSize": 100,
            "iexLastUpdated": 1607461192396,
            "delayedPrice": 28.82,
            "delayedPriceTime": 1607461198592,
            "oddLotDelayedPrice": 28.82,
            "oddLotDelayedPriceTime": 1607461198391,
            "extendedPrice": 28.93,
            "extendedChange": 0.04,
            "extendedChangePercent": 0.00137,
            "extendedPriceTime": 1607471631362,
            "previousClose": 29.49,
            "previousVolume": 42197768,
            "change": -0.16,
            "changePercent": -0.0045,
            "volume": 33820759,
            "iexMarketPercent": 0.01709376134658947,
            "iexVolume": 578127,
            "avgTotalVolume": 60029202,
            "iexBidPrice": 0,
            "iexBidSize": 0,
            "iexAskPrice": 0,
            "iexAskSize": 0,
            "iexOpen": 28.815,
            "iexOpenTime": 1607461192355,
            "iexClose": 28.815,
            "iexCloseTime": 1607461192355,
            "marketCap": 2502673458439,
            "peRatio": 14.23,
            "week52High": 34.68,
            "week52Low": 17.50,
            "ytdChange": -0.1573975163337491,
            "lastTradeTime": 1607461198587,
            "currency": "USD",
            "isUSMarketOpen": False
        }
    }
    ticker_quote = models.TickerQuote.from_iex_response(iex_data)
    quote: dict = iex_data.get("quote")
    assert str(ticker_quote.currency) == str(quote.get("currency"))
    assert str(ticker_quote.fifty_two_week_high) == str(quote.get("week52High"))
    assert str(ticker_quote.fifty_two_week_low) == str(quote.get("week52Low"))
    assert ticker_quote.is_market_open == quote.get("isUSMarketOpen")
    assert str(ticker_quote.market_cap) == str(quote.get("marketCap"))
    assert str(ticker_quote.pe_ratio) == str(quote.get("peRatio"))
    assert str(ticker_quote.price) == str(quote.get("latestPrice"))
    assert str(ticker_quote.volume) == str(quote.get("volume"))
    assert str(ticker_quote.year_to_day_change) == str(quote.get("ytdChange"))


def test_ticker_stats():
    iex_data = {
        "companyName": "Apple Inc.",
        "marketcap": 760334287200,
        "week52high": 156.65,
        "week52low": 93.63,
        "week52highSplitAdjustOnly": None,
        "week52lowSplitAdjustOnly": None,
        "week52change": 58.801903,
        "sharesOutstanding": 5213840000,
        "float": None,
        "avg10Volume": 2774000,
        "avg30Volume": 12774000,
        "day200MovingAvg": 140.60541,
        "day50MovingAvg": 156.49678,
        "employees": 120000,
        "ttmEPS": 16.5,
        "ttmDividendRate": 2.25,
        "dividendYield": .021,
        "nextDividendDate": '2019-03-01',
        "exDividendDate": '2019-02-08',
        "nextEarningsDate": '2019-01-01',
        "peRatio": 14,
        "beta": 1.25,
        "maxChangePercent": 153.021,
        "year5ChangePercent": 0.5902546932200027,
        "year2ChangePercent": 0.3777449874142869,
        "year1ChangePercent": 0.39751716851558366,
        "ytdChangePercent": 0.36659492036160124,
        "month6ChangePercent": 0.12208398133748043,
        "month3ChangePercent": 0.08466584665846649,
        "month1ChangePercent": 0.009668596145283263,
        "day30ChangePercent": -0.002762605699968781,
        "day5ChangePercent": -0.005762605699968781
        }
    ticker_stats = models.TickerStats.from_iex_response(iex_data)
    assert str(ticker_stats.beta) == str(iex_data.get("beta"))
    assert str(ticker_stats.company_name) == str(iex_data.get("companyName"))
    assert str(ticker_stats.employees) == str(iex_data.get("employees"))
    assert str(ticker_stats.fifty_day) == str(iex_data.get("day50MovingAvg"))
    assert str(ticker_stats.market_cap) == str(iex_data.get("marketcap"))
    assert str(ticker_stats.pe_ratio) == str(iex_data.get("peRatio"))
    assert str(ticker_stats.shares_outstanding) == str(iex_data.get("sharesOutstanding"))
    assert str(ticker_stats.ttm_eps) == str(iex_data.get("ttmEPS"))
    assert str(ticker_stats.two_hundred_day) == str(iex_data.get("day200MovingAvg"))
