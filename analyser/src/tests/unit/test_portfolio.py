from decimal import Decimal

from ... import models
from ...portfolio.api import PortfolioAPI


def test_calculate_holding_data(portfolio_api: PortfolioAPI):
    trades = [
        models.Trade(
            buy_or_sell=True,
            cost=10,
            date="2022-05-04",
            shares=1
        )
    ]
    ticker_data = [
        models.TickerDatum(
            change=6.309999999999945,
            change_over_time=-0.2140430644756973,
            change_percent=0.007,
            close=909.25,
            date="2022-05-03",
            volume=21236525
        ),
        models.TickerDatum(
            change=43.370000000000005,
            change_over_time=-0.17655397754285262,
            change_percent=0.0477,
            close=952.62,
            date="2022-05-04",
            volume=27214568
        ),
        models.TickerDatum(
            change=-79.34000000000003,
            change_over_time=-0.24513558135313385,
            change_percent=-0.0833,
            close=873.28,
            date="2022-05-05",
            volume=30839731
        ),
    ]
    holding_data = portfolio_api._PortfolioAPI__calculate_holding_data(ticker_data, trades)
    assert holding_data == [
        models.HoldingDatum(cost=10, date='2022-05-04', shares=1, value=952.620),
        models.HoldingDatum(cost=10, date='2022-05-05', shares=1, value=873.280)
    ]


def test_calculate_holdings_data(portfolio_api: PortfolioAPI):
    holdings = [
        models.Holding(
            symbol="TSLA",
            trades = [
                models.Trade(
                    buy_or_sell=True,
                    cost=10,
                    date="2022-05-04",
                    shares=1
                )
            ]
        )
    ]
    ticker_data_by_symbol = {
        "TSLA": [
            models.TickerDatum(
                change=6.309999999999945,
                change_over_time=-0.2140430644756973,
                change_percent=0.007,
                close=909.25,
                date="2022-05-03",
                volume=21236525
            ),
            models.TickerDatum(
                change=43.370000000000005,
                change_over_time=-0.17655397754285262,
                change_percent=0.0477,
                close=952.62,
                date="2022-05-04",
                volume=27214568
            ),
            models.TickerDatum(
                change=-79.34000000000003,
                change_over_time=-0.24513558135313385,
                change_percent=-0.0833,
                close=873.28,
                date="2022-05-05",
                volume=30839731
            ),
        ]
    }
    holdings_data_by_symbol = portfolio_api._PortfolioAPI__calculate_holdings_data(holdings, ticker_data_by_symbol)
    assert holdings_data_by_symbol == {
        "TSLA": [
            models.HoldingDatum(cost=10, date='2022-05-04', shares=1, value=952.620),
            models.HoldingDatum(cost=10, date='2022-05-05', shares=1, value=873.280)
        ]
    }


def test_calculate_portfolio_data(portfolio_api: PortfolioAPI):
    holding_data_by_symbol = {
        "TSLA": [
            models.HoldingDatum(cost=10, date='2022-05-04', shares=1, value=952.620),
            models.HoldingDatum(cost=10, date='2022-05-05', shares=1, value=873.280)
        ]
    }
    portfolio_value_by_date = portfolio_api._PortfolioAPI__calculate_portfolio_data(holding_data_by_symbol)
    assert portfolio_value_by_date == {
        '2022-05-04': Decimal('952.620'),
        '2022-05-05': Decimal('873.280'),
    }
