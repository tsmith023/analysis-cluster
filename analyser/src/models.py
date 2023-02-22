from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from pydantic import BaseModel, validator
from typing import List, Optional, Union

class Range(str, Enum):
    MAX = "max"
    FIVE_YEARS = '5y'
    TWO_YEARS = '2y'
    ONE_YEAR = '1y'
    SIX_MONTHS = '6m'
    YEAR_TO_DAY = 'ytd'


class Trade(BaseModel):
    buy_or_sell: bool
    cost: float
    date: str
    shares: float


class TradesHolding(BaseModel):
    symbol: str
    trades: List[Trade]

class PercentageHolding(BaseModel):
    symbol: str
    percentage: float

class MovingAverages(BaseModel):
    fifty_day: float
    one_hundred_day: float
    twenty_day: float
    two_hundred_day: float


class HoldingTimeseriesDatum(BaseModel):
    cost: float
    date: str
    shares: float
    value: float


class PortfolioTimeseriesDatum(BaseModel):
    cost: float
    date: str
    moving_averages: MovingAverages
    value: float


class TimeseriesResult(BaseModel):
    error: str | None = None
    id: str
    holding_timeseries_by_symbol: dict[str, list[HoldingTimeseriesDatum]] | None = None
    portfolio_timeseries: list[PortfolioTimeseriesDatum] | None = None
    range: str



class TimeseriesInputs(BaseModel):
    currency: str
    holdings: List[TradesHolding]
    id: str
    range: Range


class PerformAnalysisInputs(BaseModel):
    holdings: List[PercentageHolding]
    id: str
    range: str


class GetAnalysisInputs(BaseModel):
    id: str
    range: str

class AnalysisResult(BaseModel):
    error: str | None = None
    id: str
    range: str
    sortino_ratio: float | None = None