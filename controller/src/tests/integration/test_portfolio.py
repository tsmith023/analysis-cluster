from typing import List

from ...portfolio.api import PortfolioAPI
from ... import models


def test_get_historical_prices(portfolio_api: PortfolioAPI):
    range = "6m"
    symbol = "TSLA"
    data: dict = portfolio_api._PortfolioAPI__get_historical_prices(range, [symbol])

    assert list(data.keys()) == [symbol]

    ticker_data: List[models.TickerDatum] = data.get(symbol)
    for datum in ticker_data:
        assert type(datum) is models.TickerDatum
        assert datum.change is not None
        assert datum.change_over_time is not None
        assert datum.change_percent is not None
        assert datum.close is not None
        assert datum.date is not None
        assert datum.volume is not None
    

def test_calculate_portfolio_data(portfolio_api: PortfolioAPI):
    range = "6m"
    holdings = [
        models.Holding(
            symbol="TSLA",
            trades=[
                models.Trade(
                    buy_or_sell=True,
                    cost=10,
                    date="2022-05-04",
                    shares=1
                )
            ]
        )
    ]
    portfolio_data: List[models.PortfolioDatum] = portfolio_api.calculate_portfolio_timeseries_data(holdings, range)


    assert str(portfolio_data[0].date.date()) == "2022-05-04"

    for datum in portfolio_data:
        assert type(datum) is models.PortfolioDatum
        assert datum.date is not None
        assert datum.value is not None