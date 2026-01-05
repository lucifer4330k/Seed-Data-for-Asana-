from datetime import datetime, timedelta
import random

def get_business_day(start_date: datetime, days_offset: int) -> datetime:
    """Adds days_offset to start_date, skipping weekends."""
    current_date = start_date
    added_days = 0
    direction = 1 if days_offset > 0 else -1
    days_to_add = abs(days_offset)
    
    while added_days < days_to_add:
        current_date += timedelta(days=direction)
        # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
        if current_date.weekday() < 5:
            added_days += 1
            
    return current_date

def random_date_in_range(start: datetime, end: datetime, respect_business_days: bool = True) -> datetime:
    """Returns a random datetime between start and end."""
    if start >= end:
        return start
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    res = start + timedelta(seconds=random_seconds)
    
    if respect_business_days and res.weekday() >= 5: # Sat or Sun
        # Shift to Monday or Friday
        res += timedelta(days=(7 - res.weekday())) # Shift forward to Mon
        if res > end:
            res -= timedelta(days=3) # Shift back to Fri
            
    return res

def get_sprint_end_date(base_date: datetime) -> datetime:
    """Returns the next Friday from the base_date."""
    days_ahead = 4 - base_date.weekday() # 4 is Friday
    if days_ahead <= 0:
        days_ahead += 7
    return base_date + timedelta(days=days_ahead)
