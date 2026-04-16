# Likely Number Ranking Expansion Plan

## Goal

Extend **Lottery Edge Lab** so it does not only rank full ticket combinations, but also surfaces a more explicit **likely-number view** for the game the user is currently analyzing. The application should still avoid false guarantees while presenting a stronger mathematical weighting system across both individual numbers and combination-level candidates.

## Product direction

The upgraded ranking flow should separate three layers of scoring.

| Layer | Purpose | Output |
| --- | --- | --- |
| Number-level signal model | Score each individual number in the game field | Ranked list of likely numbers with signal breakdown |
| Candidate-pool builder | Turn number scores into a broader but controlled search space | Candidate pool for full-ticket enumeration |
| Combination-level model | Score full number sets using structural, historical, and anti-collision logic | Ranked smart picks and diversified tickets |

This lets the app answer both of the user needs now in scope. First, it can say which numbers currently score highest under the active model. Second, it can use those same scores to generate stronger ticket rankings.

## Number-level signal set

The current code already uses historical frequency, recent frequency, pair recurrence, structural windows, and collision penalties. The expansion should add a number-scoring table built from multiple mathematically relevant components.

| Signal family | Proposed implementation | Purpose |
| --- | --- | --- |
| Long-run frequency | Relative appearance rate over full history | Measures persistent historical activity |
| Recent frequency | Appearance rate over the latest rolling window | Measures short-run heat |
| Recency gap | Draws since last appearance | Supports hot/cold and overdue views |
| Rolling-trend slope | Linear regression over rolling-window hit counts | Captures upward or downward trend in recent appearance intensity |
| EWMA momentum | Exponentially weighted hit activity | Gives smoother near-term weighting than raw recent counts |
| Co-occurrence centrality | Average pair strength with other strong numbers | Rewards numbers that sit inside historically common pair structures |
| Positional tendency | Optional per-draw sorted-position statistics where relevant | Encodes exploratory position-pattern ideas from the reviewed videos |
| Collision-awareness prior | Soft penalty for highly date-like or crowd-prone values | Helps separate likely draw candidates from likely crowd picks |

The regression-style component should be deliberately lightweight and explainable. A simple line fit over rolling hit counts is preferable to an opaque model at this stage because it remains easy to inspect in the UI and more robust against overclaiming.

## Candidate-pool redesign

The current CLI candidate pool is built only from raw historical frequency. That is too narrow for the expanded product goal. The new pool builder should instead:

1. Compute the full number ranking table for the selected game.
2. Blend top-ranked numbers across several sub-signals rather than only total frequency.
3. Allow broader candidate-pool generation when a profile such as `coverage` is selected.
4. Preserve deterministic output ordering for reproducibility.

A practical approach is to create a **weighted number score** and then select the top `N` numbers by that score, optionally enforcing some diversity rules so the pool is not dominated by only hot or only overdue values.

## Combination-level model expansion

The combination-level scorer should retain backward-compatible columns while becoming richer internally.

| Existing component | Keep | Expand |
| --- | --- | --- |
| Historical frequency | Yes | Use number-score table rather than only raw counts |
| Pair recurrence | Yes | Add normalized pair-density contribution |
| Structural heuristics | Yes | Apply profile-aware windows with clearer reason tags |
| Collision-risk penalty | Yes | Extend to crowding-sensitive number patterns |
| Recent overlap penalty | Yes | Make explicit and configurable |
| Regression-style influence | New | Use aggregate trend of component numbers |
| Momentum influence | New | Use aggregate EWMA activity of component numbers |

The safest implementation is to create a `signal_breakdown` object internally, then derive the public `pattern_score`, `collision_score`, and `composite_score` from that richer structure.

## Presentation plan

The desktop application should add a dedicated tab such as **Likely Numbers** or **Weighted Number Ranking**.

That view should show a table with columns such as:

| Column | Meaning |
| --- | --- |
| Number | Candidate main-field number |
| Weighted Score | Overall number-level ranking score |
| Long-Run Freq | Historical activity score |
| Recent Heat | Recent rolling-window score |
| Trend | Linear-trend slope score |
| Momentum | EWMA score |
| Gap | Draws since last hit |
| Pair Strength | Co-occurrence contribution |
| Crowd Risk | Collision-aware crowding flag or penalty |
| Notes | Human-readable explanation of why the number ranks where it does |

The smart-pick tab should then explain that the listed tickets are assembled from the highest-weighted number pool under the selected profile.

## CLI expansion

The CLI should also expose this new logic.

| Command | New behavior |
| --- | --- |
| `rank` | Use weighted candidate-pool construction and allow profile selection |
| `recommend` | Use weighted number model before diversification |
| `backtest` | Backtest against the new candidate-pool method |
| `numbers` | New command to print ranked likely numbers and their signal breakdown |

## Guardrails

The repository can present stronger weighting while remaining legally safer if the wording is disciplined.

| Allowed framing | Avoid |
| --- | --- |
| mathematically weighted ranking | guaranteed winning numbers |
| likely-number view under current model | proven prediction engine |
| heuristic and trend-informed candidates | cheat the lottery |
| descriptive and experimental signals | certainty or promised hit rate |

## Implementation order

1. Add number-level feature calculations and snapshot outputs.
2. Add weighted number scoring and ranked-number service helpers.
3. Replace candidate-pool construction with weighted-number selection.
4. Extend combination scoring with trend and momentum aggregations.
5. Add desktop tab and CLI command for likely-number presentation.
6. Update README and test coverage.
