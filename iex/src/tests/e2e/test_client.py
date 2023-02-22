import pytest
from fastapi.testclient import TestClient
from typing import List

from ...server import app


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)


################################################
# These tests cost ~20k IEX credits to run     #
# so should only be called upon merge requests #
################################################


def test_historical_forexes(test_client: TestClient):
    symbol = "USDGBP"
    ranges = ["6m", "ytd", "1y", "2y", "5y", "max"]
    for range in ranges:
        response = test_client.get(f"/historical-forexes?range={range}&symbols={symbol}")
        data: dict = response.json()
        desired_fields = [
        "date",
        "is_derived",
        "rate",
        "timestamp", 
    ]
        assert response.status_code == 200
        assert list(data.keys()) == [symbol]
        ticker_data: List[dict] = data.get(symbol)
        for datum in ticker_data:
            for field in desired_fields:
                assert datum.get(field) is not None


def test_historical_prices(test_client: TestClient):
    symbol = "TSLA"
    ranges = ["6m", "ytd", "1y", "2y", "5y", "max"]
    for range in ranges:
        response = test_client.get(f"/historical-prices?range={range}&symbols={symbol}")
        data: dict = response.json()
        desired_fields = [
            "change",
            "change_over_time",
            "change_percent",
            "close",
            "date",
            "volume",
        ]
        assert response.status_code == 200
        assert list(data.keys()) == [symbol]
        ticker_data: List[dict] = data.get(symbol)
        for datum in ticker_data:
            for field in desired_fields:
                assert datum.get(field) is not None


def test_latest_forexes(test_client: TestClient):
    symbol = "USDGBP"
    response = test_client.get(f"/latest-forexes?symbols={symbol}")
    data: dict = response.json()
    desired_fields = [
        "date",
        "is_derived",
        "rate",
        "timestamp", 
    ]
    assert response.status_code == 200
    assert list(data.keys()) == [symbol]
    for field in desired_fields:
        assert data.get(symbol).get(field) is not None


def test_latest_quotes(test_client: TestClient):
    symbol = "TSLA"
    response = test_client.get(f"/latest-quotes?symbols={symbol}")
    data: dict = response.json()
    desired_fields = [
        "currency",
        "fifty_two_week_high",
        "fifty_two_week_low",
        "is_market_open",
        "market_cap",
        "pe_ratio",
        "price",
        "volume",
        "year_to_day_change"
    ]
    assert response.status_code == 200
    assert list(data.keys()) == [symbol]
    for field in desired_fields:
        assert data.get(symbol).get(field) is not None


def test_latest_stats(test_client: TestClient):
    symbol = "TSLA"
    response = test_client.get(f"/latest-stats?symbols={symbol}")
    data: dict = response.json()
    desired_fields = [
        "beta",
        "company_name",
        "employees",
        "fifty_day",
        "market_cap",
        "pe_ratio",
        "shares_outstanding",
        "ttm_eps",
        "two_hundred_day",
    ]
    assert response.status_code == 200
    assert list(data.keys()) == [symbol]
    for field in desired_fields:
        assert data.get(symbol).get(field) is not None