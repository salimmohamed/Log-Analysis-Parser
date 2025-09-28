"""
Timestamp parsing utilities.
"""

import re
from datetime import datetime


def is_timestamp(line: str) -> bool:
    """Check if line contains a timestamp."""
    # Match [HH:MM:SS] or [HH:MM:SS.mmm] or M/D/YYYY H:MM AM/PM or M/D/YYYY at H:MM AM/PM or "Today at H:MM AM/PM"
    return bool(
        re.match(r'\[\d{2}:\d{2}:\d{2}(\.\d{3})?\]', line.strip()) or
        re.match(r'\d{1,2}/\d{1,2}/\d{4}(\s+at)?\s+\d{1,2}:\d{2}\s*[AP]M', line.strip()) or
        re.match(r'Today at \d{1,2}:\d{2}\s*[AP]M', line.strip())
    )


def parse_timestamp(line: str) -> datetime:
    """Parse timestamp from line."""
    # Try [HH:MM:SS(.mmm)]
    match = re.search(r'\[(\d{2}:\d{2}:\d{2}(\.\d{3})?)\]', line)
    if match:
        time_str = match.group(1)
        try:
            if '.' in time_str:
                time_str, ms = time_str.split('.')
                dt = datetime.strptime(time_str, '%H:%M:%S')
                dt = dt.replace(microsecond=int(ms) * 1000)
            else:
                dt = datetime.strptime(time_str, '%H:%M:%S')
            return dt
        except ValueError:
            return None
    # Try M/D/YYYY H:MM AM/PM or M/D/YYYY at H:MM AM/PM
    match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})(?:\s+at)?\s+(\d{1,2}):(\d{2})\s*([AP]M)', line.strip())
    if match:
        month, day, year, hour, minute, ampm = match.groups()
        month, day, year, hour, minute = map(int, [month, day, year, hour, minute])
        if ampm == 'PM' and hour != 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0
        try:
            return datetime(year, month, day, hour, minute)
        except ValueError:
            return None
    
    # Try "Today at H:MM AM/PM" format
    match = re.match(r'Today at (\d{1,2}):(\d{2})\s*([AP]M)', line.strip())
    if match:
        hour, minute, ampm = match.groups()
        hour, minute = map(int, [hour, minute])
        if ampm == 'PM' and hour != 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0
        try:
            # Use today's date
            from datetime import date
            today = date.today()
            return datetime(today.year, today.month, today.day, hour, minute)
        except ValueError:
            return None
    
    return None


def parse_attempt_duration(duration_str: str) -> int:
    """Extract seconds from duration string like "(4:33)"."""
    match = re.match(r"\((\d+):(\d+)\)", duration_str)
    if match:
        minutes, seconds = map(int, match.groups())
        return minutes * 60 + seconds
    return 0
