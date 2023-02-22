from datetime import datetime
from ... import models


def test_holding_datum():
    datum = {
        "cost": 1050.1234,
        "date": "2022-06-06",
        "shares": 12.4567,
        "value": 20000,
    }
    holding_datum = models.HoldingDatum(
        cost=datum['cost'],
        date=datum['date'],
        shares=datum['shares'],
        value=datum['value'],
    )
    assert str(holding_datum.cost) == "1050.123"
    assert holding_datum.date == "2022-06-06"
    assert str(holding_datum.shares) == "12.457"
    assert str(holding_datum.value) == "20000.000"


def test_portfolio_datum():
    datum = {
        "date": "2022-06-06",
        "value": 20000,
    }
    portfolio_datum = models.PortfolioDatum(
        date=datum['date'],
        value=datum['value'],
    )
    assert portfolio_datum.date == datetime(year=2022, month=6, day=6)
    assert str(portfolio_datum.value) == "20000.000"


def test_ticker_datum():
    datum = {
        "change": 100,
        "change_percent": 0.12345,
        "change_over_time": 0.4567,
        "close": 420,
        "date": "2021-06-06",
        "volume": 10000,
    }
    ticker_datum = models.TickerDatum(
        change=datum['change'],
        change_percent=datum['change_percent'],
        change_over_time=datum['change_over_time'],
        close=datum['close'],
        date=datum['date'],
        volume=datum['volume'],
    )
    assert str(ticker_datum.change) == "100.000"
    assert str(ticker_datum.change_percent) == "0.123"
    assert str(ticker_datum.change_over_time) == "0.457"
    assert str(ticker_datum.close) == "420.000"
    assert ticker_datum.date == "2021-06-06"
    assert str(ticker_datum.volume) == "10000.000"


def test_trade():
    datum = {
        "buy_or_sell": True,
        "cost": 1050.1234,
        "date": "2022-06-06",
        "shares": 12.4567
    }
    trade = models.Trade(
        buy_or_sell=datum['buy_or_sell'],
        cost=datum['cost'],
        date=datum['date'],
        shares=datum['shares'],
    )
    assert trade.buy_or_sell == True
    assert str(trade.cost) == "1050.123"
    assert trade.date == "2022-06-06"
    assert str(trade.shares) == "12.457"
    