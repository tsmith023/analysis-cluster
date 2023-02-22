from decimal import Decimal
from enum import Enum
from pydantic import BaseModel
from typing import Union


class ForexDatum(BaseModel):
    date: str
    is_derived: bool
    fifty_day: Union[Decimal, None]
    one_hundred_day: Union[Decimal, None]
    two_hundred_day: Union[Decimal, None]
    twenty_day: Union[Decimal, None]
    rate: Decimal
    timestamp: int

    @classmethod
    def from_iex_response(cls, data: dict):
        return cls(
            date=data.get('date'),
            is_derived=data.get('isDerived'),
            fifty_day=data.get("day50MovingAverage"),
            one_hundred_day=data.get("day100MovingAverage"),
            twenty_day=data.get("day20MovingAverage"),
            two_hundred_day=data.get("day200MovingAverage"),
            rate=data.get('rate'),
            timestamp=data.get('timestamp')
        )


class Period(str, Enum):
    MAX = "max"
    FIVE_YEARS = '5y'
    TWO_YEARS = '2y'
    ONE_YEAR = '1y'
    SIX_MONTHS = '6m'
    YEAR_TO_DAY = 'ytd'

    def to_string(self) -> str:
        return str(self)
    


class TickerDatum(BaseModel):
    change: Decimal
    change_over_time: Decimal
    change_percent: Decimal
    close: Decimal
    fifty_day: Union[Decimal, None]
    one_hundred_day: Union[Decimal, None]
    two_hundred_day: Union[Decimal, None]
    twenty_day: Union[Decimal, None]
    date: str
    volume: Decimal

    @classmethod
    def from_iex_response(cls, data: dict):
        return cls(
            close=data.get('close'),
            change=data.get('change'),
            change_over_time=data.get('changeOverTime'),
            change_percent=data.get('changePercent'),
            date=data.get('date'),
            fifty_day=data.get("day50MovingAverage"),
            one_hundred_day=data.get("day100MovingAverage"),
            twenty_day=data.get("day20MovingAverage"),
            two_hundred_day=data.get("day200MovingAverage"),
            volume=data.get('volume')
        )

class TickerForexDatum(BaseModel):
    change: Decimal
    change_over_time: Decimal
    change_percent: Decimal
    close: Decimal
    date: str
    to_gbp: Decimal
    to_eur: Decimal
    to_usd: Decimal
    volume: Decimal

    @classmethod
    def from_iex_response(cls, data: dict):
        return cls(
            close=data.get('close'),
            change=data.get('change'),
            change_over_time=data.get('changeOverTime'),
            change_percent=data.get('changePercent'),
            date=data.get('date'),
            to_gbp=data.get('forexes').get('USDGBP'),
            to_eur=data.get('forexes').get('USDEUR'),
            to_usd=data.get('forexes').get('USDUSD'),
            volume=data.get('volume')
        )

class TickerQuote(BaseModel):
    currency: str | None
    fifty_two_week_high: Decimal | None
    fifty_two_week_low: Decimal | None
    is_market_open: bool | None
    market_cap: Decimal | None
    pe_ratio: Decimal | None
    price: Decimal | None
    volume: Decimal | None
    year_to_day_change: Decimal | None

    @classmethod
    def from_iex_response(cls, data: dict):
        quote: dict = data.get('quote')
        if quote is None: return None
        return cls(
            currency=quote.get('currency'),
            fifty_two_week_high=quote.get('week52High'),
            fifty_two_week_low=quote.get('week52Low'),
            is_market_open=quote.get('isUSMarketOpen'),
            market_cap=quote.get('marketCap'),
            pe_ratio=quote.get('peRatio'),
            price=quote.get('latestPrice'),
            volume=quote.get('volume'),
            year_to_day_change=quote.get('ytdChange')
        )


class TickerStats(BaseModel):
    beta: Decimal
    company_name: str
    employees: Decimal
    fifty_day: Decimal
    market_cap: Decimal
    pe_ratio: Decimal
    shares_outstanding: Decimal
    ttm_eps: Decimal
    two_hundred_day: Decimal

    @classmethod
    def from_iex_response(cls, data: dict):
        return cls(
            beta=data.get('beta'),
            company_name=data.get('companyName'),
            employees=data.get('employees'),
            fifty_day=data.get('day50MovingAvg'),
            market_cap=data.get('marketcap'),
            pe_ratio=data.get('peRatio'),
            shares_outstanding=data.get('sharesOutstanding'),
            ttm_eps=data.get('ttmEPS'),
            two_hundred_day=data.get('day200MovingAvg'),
        )