from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional, Tuple, Union
from .models import Period

def convert_date(date: str) -> Union[datetime, None]:
    if date is None: return None
    return datetime.strptime(date, "%Y-%m-%d")

def convert_period_into_datetime_period(period: Period) -> Optional[Tuple[datetime, datetime]]:
    end_date = datetime.now()
    if period == Period.MAX:
        start_date = end_date - relativedelta(years=10)
    elif period == Period.FIVE_YEARS:
        start_date = end_date - relativedelta(years=5)
    elif period == Period.TWO_YEARS:
        start_date = end_date - relativedelta(years=2)
    elif period == Period.ONE_YEAR:
        start_date = end_date - relativedelta(years=1)
    elif period == Period.SIX_MONTHS:
        start_date = end_date - relativedelta(months=6)
    elif period == Period.YEAR_TO_DAY:
        start_date = datetime(year=end_date.year, month=1, day=1)
    return start_date, end_date
    
def minutes_until_midnight():
    time_until_midnight = datetime.combine(
        datetime.now().date() + timedelta(days = 1), datetime.strptime("0000", "%H%M").time()
    ) - datetime.now()
    return (time_until_midnight.seconds // 60) % 60

def minutes_until_quarter():
    now = datetime.now()
    return 15 - now.minute % 15

def select_period(period: Period) -> str:
    if period == Period.MAX:
        return "max"
    elif period == Period.FIVE_YEARS:
        return "5y"
    elif period == Period.TWO_YEARS:
        return "2y"
    elif period == Period.ONE_YEAR:
        return "1y"
    elif period == Period.SIX_MONTHS:
        return "6m"
    elif period == Period.YEAR_TO_DAY:
        return "ytd"
    else:
        return "ytd"