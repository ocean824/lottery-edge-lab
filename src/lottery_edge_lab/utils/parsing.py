from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable, List


def parse_int_list(raw: str | Iterable[int]) -> List[int]:
    if isinstance(raw, str):
        return [int(part) for part in re.findall(r"\d+", raw)]
    return [int(value) for value in raw]


def parse_date(value: str) -> str:
    value = value.strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%Y, %b %d", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def sort_main_numbers(numbers: Iterable[int]) -> list[int]:
    return sorted(int(n) for n in numbers)
