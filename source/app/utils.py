from datetime import time, datetime
from typing import List, Tuple


def unpack_time(hours: List[str]) -> List[Tuple[time, time]]:
    time_arr = []
    for t in hours:
        t1, t2 = map(lambda e: datetime.strptime(e, "%H:%M").time(), t.split('-'))
        time_arr.append((t1, t2))
    return time_arr


def time_to_str(t: datetime):
    return t.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4] + "Z"


def str_to_time(s: str):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
