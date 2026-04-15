from __future__ import annotations

import io
import re
from dataclasses import asdict
from datetime import datetime, timezone
from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup

from lottery_edge_lab.registry import get_game
from lottery_edge_lab.utils.parsing import parse_int_list, sort_main_numbers

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_megamillions_from_ny_open_data(limit: int | None = None) -> pd.DataFrame:
    game = get_game("megamillions")
    url = "https://data.ny.gov/api/views/5xaw-6ayf/rows.csv?accessType=DOWNLOAD"
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=30)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    df = df.rename(columns={
        "Draw Date": "draw_date",
        "Winning Numbers": "winning_numbers",
        "Mega Ball": "bonus_ball",
        "Multiplier": "multiplier",
    })
    records: List[dict] = []
    for row in df.to_dict(orient="records"):
        main_numbers = sort_main_numbers(parse_int_list(str(row["winning_numbers"])))
        records.append(
            {
                "country": game.country,
                "jurisdiction": "new_york_open_data",
                "game_name": game.game_name,
                "game_slug": game.game_slug,
                "draw_date": pd.to_datetime(row["draw_date"]).date().isoformat(),
                "main_numbers": " ".join(map(str, main_numbers)),
                "bonus_numbers": str(int(row["bonus_ball"])),
                "multiplier": str(row.get("multiplier", "")).zfill(2),
                "source_name": "ny_open_data_megamillions",
                "source_url": url,
                "ingested_at": _timestamp(),
            }
        )
    out = pd.DataFrame(records).sort_values("draw_date")
    if limit:
        out = out.tail(limit)
    return out.reset_index(drop=True)


def fetch_megamillions_official(limit: int = 100) -> pd.DataFrame:
    game = get_game("megamillions")
    url = "https://www.megamillions.com/winning-numbers/previous-drawings.aspx"
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    pattern = re.compile(r"^(\d{1,2}/\d{1,2}/\d{4})(\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2})(\d{1,2})(?:N/A|(\d+))")
    records: List[dict] = []
    seen_dates = set()
    for anchor in soup.find_all("a"):
        text = " ".join(anchor.get_text(" ", strip=True).split())
        match = pattern.match(text.replace(" + ", " "))
        if not match:
            continue
        draw_date, main_raw, bonus_raw, multiplier = match.groups()
        if draw_date in seen_dates:
            continue
        seen_dates.add(draw_date)
        records.append(
            {
                "country": game.country,
                "jurisdiction": game.jurisdiction,
                "game_name": game.game_name,
                "game_slug": game.game_slug,
                "draw_date": pd.to_datetime(draw_date).date().isoformat(),
                "main_numbers": " ".join(map(str, sort_main_numbers(parse_int_list(main_raw)))),
                "bonus_numbers": str(int(bonus_raw)),
                "multiplier": multiplier or "",
                "source_name": "official_megamillions_html",
                "source_url": url,
                "ingested_at": _timestamp(),
            }
        )
    out = pd.DataFrame(records).sort_values("draw_date")
    if limit:
        out = out.tail(limit)
    return out.reset_index(drop=True)


def fetch_powerball_from_nc(limit: int = 200) -> pd.DataFrame:
    game = get_game("powerball")
    url = "https://nclottery.com/powerball-past-draws"
    tables = pd.read_html(url)
    if not tables:
        raise ValueError("No tables found on NC Powerball archive page.")
    df = tables[0].copy()
    df.columns = [str(col).strip().lower() for col in df.columns]
    if "date" not in df.columns or "results" not in df.columns:
        raise ValueError("Expected columns not found in NC Powerball table.")
    records: List[dict] = []
    for row in df.to_dict(orient="records"):
        date_text = str(row.get("date", "")).strip()
        if not re.match(r"^\d{4},\s+[A-Z][a-z]{2}\s+\d{1,2}$", date_text):
            continue
        values = parse_int_list(str(row.get("results", "")))
        if len(values) < 6:
            continue
        main_numbers = sort_main_numbers(values[:5])
        bonus_ball = values[5]
        multiplier_match = re.search(r"(\d+)x", str(row.get("results", "")), flags=re.IGNORECASE)
        records.append(
            {
                "country": game.country,
                "jurisdiction": "north_carolina_official",
                "game_name": game.game_name,
                "game_slug": game.game_slug,
                "draw_date": datetime.strptime(date_text, "%Y, %b %d").replace(year=int(date_text[:4])).date().isoformat(),
                "main_numbers": " ".join(map(str, main_numbers)),
                "bonus_numbers": str(int(bonus_ball)),
                "multiplier": multiplier_match.group(1) if multiplier_match else "",
                "source_name": "nc_powerball_archive",
                "source_url": url,
                "ingested_at": _timestamp(),
            }
        )
    out = pd.DataFrame(records).sort_values("draw_date")
    if limit:
        out = out.tail(limit)
    return out.reset_index(drop=True)


def fetch_game_history(game_slug: str, limit: int | None = None) -> pd.DataFrame:
    if game_slug == "megamillions":
        try:
            return fetch_megamillions_from_ny_open_data(limit=limit)
        except Exception:
            fallback_limit = limit or 100
            return fetch_megamillions_official(limit=fallback_limit)
    if game_slug == "powerball":
        fallback_limit = limit or 200
        return fetch_powerball_from_nc(limit=fallback_limit)
    raise ValueError(f"Unsupported game source fetch for '{game_slug}'.")
