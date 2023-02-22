from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, Tuple
from .models import Range

def convert_range_into_datetime_period(range: Range) -> Optional[Tuple[datetime, datetime]]:
    end_date = datetime.now()
    if range == Range.MAX:
        start_date = end_date - relativedelta(years=10)
    elif range == Range.FIVE_YEARS:
        start_date = end_date - relativedelta(years=5)
    elif range == Range.TWO_YEARS:
        start_date = end_date - relativedelta(years=2)
    elif range == Range.ONE_YEAR:
        start_date = end_date - relativedelta(years=1)
    elif range == Range.SIX_MONTHS:
        start_date = end_date - relativedelta(months=6)
    elif range == Range.YEAR_TO_DAY:
        start_date = datetime(year=end_date.year, month=1, day=1)
    return start_date, end_date