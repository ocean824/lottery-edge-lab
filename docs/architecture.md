# Lottery Edge Lab: Product Scope and Architecture

## Overview

**Lottery Edge Lab** is a research-driven Python toolkit for ingesting, normalizing, analyzing, and ranking lottery combinations across local, state, and national draw games. The design goal is not to promise deterministic prediction of future winning combinations. Instead, it combines three mathematically grounded layers: structured multi-source data ingestion, probabilistic ranking of candidate combinations using historical features, and **expected-value optimization** through collision-risk reduction and ticket-coverage design.[1] [2] [3] [4]

The architecture is built around the observation that lottery data is fragmented across official national sites, state archives, public open-data catalogs, and third-party aggregation services. Official archives for Powerball and Mega Millions expose searchable historical results, while some state or open-data portals also expose machine-readable CSV or JSON resources.[5] [6] [7] [8] A scalable tool therefore needs source adapters, canonical schemas, provenance tracking, and validation logic rather than one-off scraping.

## Research-backed design principles

The repository will be organized around a distinction between **draw randomness** and **player behavior**. Under fair lottery drawings, historical winning numbers do not provide strong evidence for reliable deterministic prediction. By contrast, player behavior is observably non-uniform: people prefer birth-date numbers, date-related values, and centrally positioned numbers, while play behavior also reacts to recent draws.[3] This means the strongest practical edge may come from reducing how often a chosen ticket is shared, combined with careful jackpot and payout analysis, rather than from claiming to foresee the exact next draw.[1] [2] [3]

Commercial lottery systems commonly market hot and cold numbers, overdue numbers, wheeling, and AI-driven pattern analysis. Of these, the most defensible components are **coverage optimization** and **collision reduction**. Wheeling helps distribute a selected number pool across tickets more efficiently, while expected-value models can evaluate when jackpot size and sharing risk make a play more attractive.[1] [4]

## System architecture

| Layer | Purpose | Core outputs |
| --- | --- | --- |
| Source adapters | Retrieve draw history from official or fallback sources | Raw source records |
| Normalization pipeline | Convert heterogeneous records to one canonical schema | Validated draw records |
| Feature engineering | Compute frequency, recency, co-occurrence, entropy, spacing, and sum-band features | Modeling tables |
| Candidate generation | Produce candidate number sets by game rules | Candidate combinations |
| Scoring engine | Rank candidates using weighted statistical models | Ranked combinations |
| Collision-risk model | Estimate how likely a ticket is to be commonly chosen by players | Collision score |
| Ticket portfolio optimizer | Build wheels and diversified bundles under a budget | Ticket portfolio |
| Backtesting and simulation | Evaluate calibration and historical performance | Metrics and reports |

## Data-source strategy

The ingestion layer should prioritize sources by reliability and structure.

| Priority | Source type | Rationale | Typical examples |
| --- | --- | --- | --- |
| 1 | Official downloadable datasets | Stable, machine-readable, lower parser fragility | Government or state CSV/JSON feeds such as the New York open-data Mega Millions dataset[8] |
| 2 | Official archive pages | Source-of-truth result history when downloads are unavailable | Official Powerball and Mega Millions archive pages[5] [6] |
| 3 | State lottery archive pages | Broad jurisdiction coverage, often with game-specific history | North Carolina archive pages and similar state sites[7] |
| 4 | Third-party aggregation APIs | Coverage fallback for unsupported lotteries | Commercial US lottery APIs discovered during research |

Every ingested record should preserve `source_name`, `source_url`, `retrieved_at`, `jurisdiction`, `game_name`, and a validation hash so that downstream analysis remains auditable.

## Canonical data model

The normalized schema should support both fixed-format jackpot games and smaller draw games.

| Field | Description |
| --- | --- |
| `jurisdiction` | State, city, region, or national authority |
| `country` | Country code, defaulting initially to `US` |
| `game_name` | Human-readable game name |
| `game_slug` | Stable internal identifier |
| `draw_date` | Draw date in ISO format |
| `draw_time` | Optional draw time if available |
| `main_numbers` | Ordered list of primary numbers |
| `bonus_numbers` | Ordered list of bonus numbers, if any |
| `multiplier` | Optional multiplier such as Power Play or Megaplier |
| `jackpot_estimate` | Optional announced jackpot estimate |
| `annuity_estimate` | Optional annuity value |
| `cash_value_estimate` | Optional cash option value |
| `source_name` | Name of source system |
| `source_url` | Record or dataset source |
| `raw_payload` | Preserved raw source payload |
| `ingested_at` | Timestamp of normalization |

Game definitions should live separately in a registry so that the engine knows each game’s ball ranges, main-number count, bonus-ball count, and optional multipliers.

## Modeling approach

The repository should implement a layered scoring model rather than a single prediction claim. The first layer is a **historical-pattern scorer** that produces descriptive and weakly predictive features, including rolling frequency, recent absence, pair and triplet co-occurrence, number dispersion, odd-even balance, low-high balance, sum bands, and repeated-digit motifs. These features can rank candidate sets, but must be evaluated with backtesting rather than treated as proof of forecast power.

The second layer is a **collision-risk scorer**. Since lottery players favor certain numbers and aesthetically balanced combinations, the model should penalize combinations that look overly popular, such as date-heavy sets or visually central clusters.[3] This can improve expected payout conditional on a win even when the draw itself remains random.

The third layer is a **portfolio optimizer**. Given a game, a budget, and an optional number pool, the optimizer should build either a diversified ticket set or a wheeled structure that maximizes coverage subject to cost. This converts research-backed logic into an execution system instead of a vague pattern claim.[4]

## Execution logic

The recommended execution flow is as follows.

| Step | Action | Result |
| --- | --- | --- |
| 1 | Load registered lottery definitions | Game rules become available |
| 2 | Run source adapters for selected jurisdictions/games | Raw draw histories are collected |
| 3 | Normalize and validate records | Canonical dataset is produced |
| 4 | Build feature tables per game | Historical signals become queryable |
| 5 | Generate candidate combinations | Search space is created |
| 6 | Score candidates with pattern model | Base ranking is assigned |
| 7 | Score collision risk | Overly popular combinations are penalized |
| 8 | Apply portfolio or wheel optimizer | Ticket bundles are constructed |
| 9 | Backtest and simulate | Outputs are evaluated historically |
| 10 | Export ranked tickets and diagnostics | Usable recommendations are produced |

## Initial product scope for version 1

The first implementation should focus on U.S. draw lotteries while keeping the connector framework extensible. Version 1 should support a configurable set of official or semi-official sources, including at minimum Powerball, Mega Millions, and one or more state-lottery archives or open-data feeds. The codebase should also be able to add daily numbers games later through new game definitions and adapters.

## Repository structure

```text
lottery-edge-lab/
├── README.md
├── pyproject.toml
├── requirements.txt
├── src/lottery_edge_lab/
│   ├── cli.py
│   ├── config.py
│   ├── registry.py
│   ├── models/
│   ├── data_sources/
│   ├── ingest/
│   ├── features/
│   ├── scoring/
│   ├── optimization/
│   ├── backtest/
│   └── utils/
├── data/
│   ├── raw/
│   ├── normalized/
│   └── processed/
├── notebooks/
├── tests/
└── docs/
```

## Product-positioning language

The repository documentation should describe the output as a **statistical edge engine** or **research-oriented ranking system** rather than a guaranteed predictor. This is both more accurate and more credible. The tool can still surface "top-ranked combinations" for the next draw, but those rankings should be presented with backtest statistics, uncertainty, and the distinction between descriptive patterns and expected-value optimization.

## References

[1]: https://arxiv.org/abs/2101.04242 "Maximizing the Expected Value of a Lottery Ticket: How to Sell and When to Buy"
[2]: https://web.williams.edu/Economics/wp/mathesonlottery.pdf "In Search of a Fair Bet in the Lottery"
[3]: https://www.cambridge.org/core/journals/judgment-and-decision-making/article/number-preferences-in-lotteries/47BA27051627CEED421AD3AEE255521E "Number preferences in lotteries"
[4]: https://lottoexpert.net/picking-winning-numbers/lottery-wheeling-systems "Lottery Wheeling Systems | Structured Coverage Explained Clearly"
[5]: https://www.powerball.com/previous-results "Previous Results | Powerball"
[6]: https://www.megamillions.com/winning-numbers/previous-drawings.aspx "Previous Drawings | Mega Millions"
[7]: https://nclottery.com/powerball-past-draws "Powerball - Past Draws | NC Education Lottery"
[8]: https://catalog.data.gov/dataset/lottery-mega-millions-winning-numbers-beginning-2002 "Lottery Mega Millions Winning Numbers: Beginning 2002"
