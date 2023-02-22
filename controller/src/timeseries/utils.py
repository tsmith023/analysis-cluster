from datetime import datetime, timedelta

def convert_date(date: str) -> datetime | None:
    if date is None: return None
    return datetime.strptime(date, "%Y-%m-%d")


def minutes_until_midnight():
    time_until_midnight = datetime.combine(
        datetime.now().date() + timedelta(days = 1), datetime.strptime("0000", "%H%M").time()
    ) - datetime.now()
    return (time_until_midnight.seconds // 60) % 60

def minutes_until_quarter():
    now = datetime.now()
    return 15 - now.minute % 15