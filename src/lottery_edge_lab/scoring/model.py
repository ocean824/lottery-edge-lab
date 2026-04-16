from __future__ import annotations

from itertools import combinations

import pandas as pd

from lottery_edge_lab.features.engineering import build_feature_snapshot, candidate_features
from lottery_edge_lab.heuristics import HeuristicProfile, get_profile, values_overlap_count



def collision_risk_score(candidate: list[int]) -> float:
    ordered = sorted(candidate)
    all_leq_31_penalty = 1.5 if all(number <= 31 for number in ordered) else 0.0
    date_heavy_penalty = sum(1 for number in ordered if number <= 12) * 0.15
    center_bias_penalty = sum(1 for number in ordered if 20 <= number <= 40) * 0.05
    repeated_terminal_penalty = 0.2 if len({number % 10 for number in ordered}) <= 3 else 0.0
    consecutive_penalty = sum(1 for a, b in zip(ordered[:-1], ordered[1:]) if b - a == 1) * 0.1
    return round(all_leq_31_penalty + date_heavy_penalty + center_bias_penalty + repeated_terminal_penalty + consecutive_penalty, 4)



def heuristic_profile_score(candidate: list[int], snapshot: dict, profile: HeuristicProfile) -> tuple[float, list[str]]:
    features = candidate_features(candidate)
    score = 0.0
    notes: list[str] = []

    if profile.sum_min is not None and features["sum"] < profile.sum_min:
        score -= 0.5
        notes.append(f"sum<{profile.sum_min}")
    elif profile.sum_max is not None and features["sum"] > profile.sum_max:
        score -= 0.5
        notes.append(f"sum>{profile.sum_max}")
    else:
        score += 0.25

    if profile.range_min is not None and features["range"] < profile.range_min:
        score -= 0.35
        notes.append(f"range<{profile.range_min}")
    elif profile.range_max is not None and features["range"] > profile.range_max:
        score -= 0.2
        notes.append(f"range>{profile.range_max}")
    else:
        score += 0.2

    if profile.odd_count_min is not None and features["odd_count"] < profile.odd_count_min:
        score -= 0.25
        notes.append("odd imbalance")
    elif profile.odd_count_max is not None and features["odd_count"] > profile.odd_count_max:
        score -= 0.25
        notes.append("odd imbalance")
    else:
        score += 0.2

    if profile.low_count_min is not None and features["low_count"] < profile.low_count_min:
        score -= 0.2
        notes.append("low/high imbalance")
    elif profile.low_count_max is not None and features["low_count"] > profile.low_count_max:
        score -= 0.2
        notes.append("low/high imbalance")
    else:
        score += 0.15

    if profile.ac_min is not None and features["ac_value"] < profile.ac_min:
        score -= 0.25
        notes.append(f"ac<{profile.ac_min}")
    elif profile.ac_max is not None and features["ac_value"] > profile.ac_max:
        score -= 0.25
        notes.append(f"ac>{profile.ac_max}")
    else:
        score += 0.15

    if profile.max_consecutive_pairs is not None and features["consecutive_pairs"] > profile.max_consecutive_pairs:
        score -= 0.15
        notes.append("too many consecutive pairs")

    recent_draws = snapshot.get("recent_draws", [])
    if profile.avoid_recent_overlap and recent_draws:
        latest = recent_draws[-1]
        overlap = values_overlap_count(candidate, latest)
        if overlap >= max(2, len(candidate) // 2):
            score -= 0.25
            notes.append("heavy overlap with latest draw")

    return round(score, 6), notes



def historical_pattern_score(candidate: list[int], snapshot: dict, profile_slug: str | None = None) -> tuple[float, list[str]]:
    profile = get_profile(profile_slug)
    features = candidate_features(candidate)
    main_frequency = snapshot["main_frequency"]
    pair_frequency = snapshot["pair_frequency"]
    recent_frequency = snapshot["recent_frequency"]
    draw_count = max(snapshot["draw_count"], 1)

    freq_score = sum(main_frequency.get(number, 0) / draw_count for number in candidate)
    pair_score = sum(pair_frequency.get(tuple(sorted(pair)), 0) / draw_count for pair in combinations(candidate, 2))
    recency_penalty = sum(recent_frequency.get(number, 0) / 10 for number in candidate) * 0.15
    structure_bonus = 0.0

    if 2 <= features["odd_count"] <= 3:
        structure_bonus += 0.3
    if 1 <= features["low_count"] <= len(candidate) - 1:
        structure_bonus += 0.1
    if features["consecutive_pairs"] <= 1:
        structure_bonus += 0.1
    if 100 <= features["sum"] <= 220:
        structure_bonus += 0.2
    if features["range"] >= 25:
        structure_bonus += 0.15

    heuristic_score, notes = heuristic_profile_score(candidate, snapshot, profile)
    total = round(freq_score + pair_score + structure_bonus + heuristic_score - recency_penalty, 6)
    return total, notes



def rank_candidates(candidates: list[list[int]], history_df: pd.DataFrame, profile_slug: str | None = None) -> pd.DataFrame:
    snapshot = build_feature_snapshot(history_df)
    ranked_rows = []
    for candidate in candidates:
        ordered = sorted(candidate)
        pattern_score, _notes = historical_pattern_score(ordered, snapshot, profile_slug=profile_slug)
        collision_score = collision_risk_score(ordered)
        composite_score = round(pattern_score - collision_score, 6)
        ranked_rows.append(
            {
                "numbers": " ".join(map(str, ordered)),
                "pattern_score": pattern_score,
                "collision_score": collision_score,
                "composite_score": composite_score,
            }
        )
    ranked = pd.DataFrame(ranked_rows)
    return ranked.sort_values(["composite_score", "pattern_score"], ascending=False).reset_index(drop=True)
