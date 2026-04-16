from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class HeuristicProfile:
    slug: str
    title: str
    description: str
    sum_min: int | None = None
    sum_max: int | None = None
    range_min: int | None = None
    range_max: int | None = None
    odd_count_min: int | None = None
    odd_count_max: int | None = None
    low_count_min: int | None = None
    low_count_max: int | None = None
    ac_min: int | None = None
    ac_max: int | None = None
    max_consecutive_pairs: int | None = None
    avoid_recent_overlap: bool = False
    notes: str = ""


PROFILES: dict[str, HeuristicProfile] = {
    "balanced": HeuristicProfile(
        slug="balanced",
        title="Balanced historical profile",
        description="Uses broad historical-shape filters commonly discussed in lottery-analysis communities.",
        sum_min=120,
        sum_max=220,
        range_min=25,
        odd_count_min=2,
        odd_count_max=3,
        low_count_min=2,
        low_count_max=3,
        ac_min=7,
        ac_max=10,
        max_consecutive_pairs=1,
        notes="This profile operationalizes descriptive heuristics only. It does not make future draws predictable.",
    ),
    "strict": HeuristicProfile(
        slug="strict",
        title="Strict pattern filter",
        description="A narrower filter inspired by the more restrictive video examples for sum, spread, parity, and AC.",
        sum_min=150,
        sum_max=200,
        range_min=40,
        range_max=60,
        odd_count_min=2,
        odd_count_max=3,
        low_count_min=2,
        low_count_max=3,
        ac_min=8,
        ac_max=9,
        max_consecutive_pairs=1,
        avoid_recent_overlap=True,
        notes="This is a high-rejection heuristic profile derived from popular lottery-filtering content.",
    ),
    "coverage": HeuristicProfile(
        slug="coverage",
        title="Coverage and diversification profile",
        description="Favors wider distribution and lower crowding risk rather than narrow historical-shape matching.",
        sum_min=110,
        sum_max=230,
        range_min=35,
        odd_count_min=2,
        odd_count_max=4,
        low_count_min=1,
        low_count_max=4,
        ac_min=6,
        ac_max=10,
        max_consecutive_pairs=1,
        notes="Useful when building multiple tickets and trying to diversify structural exposure.",
    ),
}


def list_profiles() -> list[HeuristicProfile]:
    return list(PROFILES.values())



def get_profile(profile_slug: str | None) -> HeuristicProfile:
    if not profile_slug:
        return PROFILES["balanced"]
    try:
        return PROFILES[profile_slug]
    except KeyError as exc:
        raise ValueError(f"Unknown heuristic profile: {profile_slug}") from exc



def describe_profile(profile_slug: str | None) -> str:
    profile = get_profile(profile_slug)
    return f"{profile.title}: {profile.description} {profile.notes}".strip()



def profile_summary_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for profile in list_profiles():
        rows.append(
            {
                "slug": profile.slug,
                "title": profile.title,
                "description": profile.description,
                "sum_window": _render_range(profile.sum_min, profile.sum_max),
                "spread_window": _render_range(profile.range_min, profile.range_max),
                "odd_count": _render_range(profile.odd_count_min, profile.odd_count_max),
                "low_count": _render_range(profile.low_count_min, profile.low_count_max),
                "ac_window": _render_range(profile.ac_min, profile.ac_max),
            }
        )
    return rows



def _render_range(lower: int | None, upper: int | None) -> str:
    if lower is None and upper is None:
        return "Any"
    if lower is not None and upper is not None:
        return f"{lower}-{upper}"
    if lower is not None:
        return f">= {lower}"
    return f"<= {upper}"



def values_overlap_count(values: Iterable[int], reference: Iterable[int]) -> int:
    return len(set(values).intersection(set(reference)))
