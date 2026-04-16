# Video Strategy Classification Memo

The reviewed video sources suggest that the repository should distinguish between three layers of logic: **grounded math**, **heuristic filtering**, and **unsupported performance claims**.

## Grounded methods worth preserving as first-class features

These methods are mathematically legitimate even if they do not create true predictive power for future random draws.

| Category | Method | Rationale | Recommended product treatment |
| --- | --- | --- | --- |
| Descriptive statistics | Sum, spread, odd/even balance, high/low balance, frequency tables, pair counts | These accurately describe historical draws | Expose directly in charts, tables, and pick-profile summaries |
| Combinatorics | Total combinations, jackpot odds, ticket-space size | Rules-based and exact under configured game structure | Keep in jackpot analysis and prize/odds views |
| Collision-risk modeling | Penalizing date-heavy picks and common human biases | Does not change win odds, but can reduce split-risk if a ticket wins | Keep as a separate explanation layer in smart-pick logic |
| Positive-EV monitoring | Roll-down thresholds, ticket cost vs expected payout | Legitimate only for rare game structures with special rules | Add as an optional EV monitor module, not a general promise |
| Portfolio construction | Diversification and overlap control across generated tickets | Useful for organizing multiple picks | Keep and extend in wheel/portfolio tooling |

## Heuristic methods that are codeable but unproven as prediction engines

These are implementable and useful as configurable constraints, but they should be framed as **heuristic profiles** rather than validated forecasting.

| Heuristic | Typical video rule | Implementation decision |
| --- | --- | --- |
| Sum window | 120 to 220, often 150 to 200 | Add configurable filter and profile presets |
| Spread window | Often 40 to 60 | Add configurable filter and profile presets |
| Odd/even parity | 3:2 or 2:3 | Add configurable filter and profile presets |
| High/low balance | At least two low and two high | Add configurable filter and profile presets |
| AC value | Often 8 to 10 | Add AC calculation and optional target range filter |
| Hot-number tilt | Favor recently frequent numbers | Add weight control in ranking/generation |
| Anti-clustering | Avoid tight grouping and excess consecutives | Add penalty/constraint control |
| Uniqueness | Avoid repeated generated sets and optionally recent actual draws | Add uniqueness guardrail in ticket generation |
| LLM prompt export | Provide structured statistics for optional outside-model prompting | Add export helper, but do not embed claims of predictive validity |

## Risky or unsupported claims that should not be treated as validated facts

The videos repeatedly claim or imply that AI can predict 4+1 outcomes, materially raise winning rates, discover hidden red-ball formulas, or convert lottery forecasting into a feasible system. These claims are not substantiated by the source material itself. They may still be documented in research notes, but the application should not present them as proven outcomes.

> The safest product posture is that the software offers **analysis, filtering, portfolio design, and informational heuristics**. It does not alter the randomness of the draw or guarantee better outcomes.

## Implementation shortlist for the next code pass

The most valuable additions are a new heuristic-profile engine, AC-value computation, optional uniqueness constraints, filter-aware smart-pick generation, and an EV-watch concept for rare special-rule games. Documentation should explain that these additions operationalize common community strategies without representing them as verified predictive science.
