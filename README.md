# Lottery Edge Lab

**Lottery Edge Lab** is a private, research-oriented Python repository for ingesting draw history across lottery sources, ranking candidate combinations, estimating collision risk, and generating wheel-style ticket portfolios. The project is intentionally framed as a **statistical edge** tool rather than a deterministic prophecy engine. The underlying research reviewed during setup indicates that the most defensible lottery advantages tend to come from **expected-value analysis, reduced ticket collisions, and structured coverage**, not from a verified ability to forecast a fair random draw with certainty.[1] [2] [3] [4]

## Why this repository exists

Many lottery systems advertise hot numbers, cold numbers, overdue numbers, AI prediction, delta systems, and wheel generators. The research picture is more nuanced. Official national and state archives make historical draw data available, and at least some government data portals expose machine-readable datasets for lottery results.[5] [6] [7] [8] That means serious analysis is possible. However, the most rigorous sources reviewed for this project suggest that practical edge is more plausibly created by improving **ticket selection strategy** and **portfolio structure** than by claiming certain foresight over the next draw.[1] [2] [3]

This repository is therefore designed to do four things well. First, it retrieves and normalizes historical lottery data. Second, it derives pattern-based features from real draw history. Third, it penalizes combinations that look unusually popular or likely to be shared. Fourth, it converts ranked combinations into more disciplined ticket sets and abbreviated wheels.

## Research grounding

The repository design follows several research-backed observations.

| Observation | Implication for the repository |
| --- | --- |
| Lottery archives exist across official national pages, state pages, and public data portals.[5] [6] [7] [8] | The codebase needs connector-style ingestion and a canonical schema. |
| Expected value can improve when jackpot size is high enough and ticket collisions are reduced.[1] [2] | The system should include collision-aware ranking and expected-value oriented logic. |
| Lottery players choose numbers non-uniformly, often favoring dates, meaningful numbers, and certain layout positions.[3] | The system should penalize date-heavy or otherwise popular-looking combinations. |
| Wheeling is best understood as coverage optimization rather than draw prediction.[4] | The system should include wheel generation, but document it as portfolio structure. |

> “We find that choice is far from uniform, and exhibits some familiar and some new tendencies and biases. Players favor personally meaningful and situationally available numbers...” — *Number preferences in lotteries*[3]

> “Thus, the expected value of a lottery ticket decreases as the probability of collisions ... increase.” — *Maximizing the Expected Value of a Lottery Ticket: How to Sell and When to Buy*[1]

## Current scope

Version 0.1.0 focuses on **U.S. draw lotteries** with an extensible source-adapter architecture. The repository currently includes live connectors for:

| Game | Initial source strategy | Source type |
| --- | --- | --- |
| Mega Millions | New York open-data CSV, with official-page fallback | Official machine-readable data plus official archive fallback |
| Powerball | North Carolina official archive page | Official state archive |

The architecture is intentionally broader than the current adapter count. It is structured so you can continue adding local, municipal, state, and national lotteries by creating new source adapters and new game definitions.

## Repository layout

```text
lottery-edge-lab/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── docs/
│   └── architecture.md
├── src/lottery_edge_lab/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── ingest.py
│   ├── registry.py
│   ├── data_sources/
│   ├── features/
│   ├── scoring/
│   ├── optimization/
│   ├── backtest/
│   └── utils/
├── data/
│   ├── raw/
│   ├── normalized/
│   └── processed/
└── tests/
    └── test_smoke.py
```

## Methodology

The workflow is organized into three analytical layers.

### 1. Historical-pattern ranking

The ranking engine computes descriptive features from historical draws, including single-number frequency, pair co-occurrence, recency pressure, odd-even balance, sum ranges, spacing, and spread. These features do **not** prove forecastability. They are used as a disciplined ranking heuristic that can be backtested.

### 2. Collision-risk scoring

The collision model penalizes combinations that are more likely to be popular among other players. In the current implementation, it downranks tickets that are date-heavy, excessively concentrated in the central range, strongly repetitive in terminal digits, or otherwise visually conventional. This is a direct implementation of the player-preference finding that number choice is not uniform.[3]

### 3. Portfolio and wheel optimization

The optimizer converts ranked candidates into more diversified tickets or into abbreviated wheel-style structures. This reflects the mathematically sensible core of wheeling systems: they help structure coverage once a number pool has already been selected.[4]

## Command-line interface

After dependencies are installed, the repository can be run either as a module or through an installed command entry point.

| Command | Purpose | Example |
| --- | --- | --- |
| `sync` | Fetch and store normalized draw history | `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli sync --game megamillions --limit 80` |
| `rank` | Rank candidate combinations from a historical pool | `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli rank --game powerball --pool-size 10 --top 20` |
| `recommend` | Produce diversified recommended tickets | `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli recommend --game megamillions --pool-size 10 --ticket-count 5` |
| `backtest` | Run a rolling backtest on ranked candidates | `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli backtest --game megamillions --pool-size 10 --top-n 10 --train-window 30` |
| `wheel` | Build an abbreviated wheel from a custom number pool | `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli wheel --pool 3,7,12,18,23,29,33 --ticket-size 5 --limit 12` |

## Installation

Clone the repository and install the runtime dependencies.

```bash
git clone <your-private-repo-url>
cd lottery-edge-lab
python3.11 -m pip install -r requirements.txt
export PYTHONPATH=src
```

If your environment supports package installation for local projects, you may also install the repository itself with `python3.11 -m pip install .`. The direct `PYTHONPATH=src` workflow is documented as the default because it is the most portable across locked-down environments.

## Example workflow

The most useful initial workflow is to sync a game, inspect top-ranked candidates, and then generate a more diversified ticket set.

```bash
PYTHONPATH=src python3.11 -m lottery_edge_lab.cli sync --game megamillions --limit 80
PYTHONPATH=src python3.11 -m lottery_edge_lab.cli rank --game megamillions --pool-size 10 --top 10
PYTHONPATH=src python3.11 -m lottery_edge_lab.cli recommend --game megamillions --pool-size 10 --ticket-count 5 --max-overlap 2
```

If you already have a custom number pool and want structure rather than a fresh ranking pass, use the wheel command.

```bash
PYTHONPATH=src python3.11 -m lottery_edge_lab.cli wheel --pool 3,7,12,18,23,29,33 --ticket-size 5 --limit 10
```

## Example local validation snapshot

Using live-source histories pulled during repository setup, the current prototype produced the following **illustrative** rolling backtest outputs.

| Game | Historical rows used | Train window | Mean best overlap within top-N | Top-N hit rate for 3+ matches |
| --- | --- | --- | --- | --- |
| Mega Millions | 80-row sync with 50 evaluation rows | 30 | 0.88 | 0.02 |
| Powerball | Smaller archive sample with 15 evaluation rows | 15 | 1.47 | 0.20 |

These numbers should be read carefully. They are **example prototype diagnostics**, not evidence of a verified winning-number prediction system. The Powerball sample is materially smaller than the Mega Millions sample, and both results depend on the current candidate-pool generation strategy and the limited prototype feature set.

## Limitations

The repository is deliberately explicit about its limits.

| Limitation | Practical meaning |
| --- | --- |
| Fair drawings remain close to random | No module here can honestly guarantee future winning numbers |
| Current adapters are not yet exhaustive | The architecture supports many lotteries, but each new source still needs a connector |
| Historical features may overfit | Backtests are necessary and should be expanded before trust is increased |
| Collision-risk modeling is approximate | It uses behavioral heuristics, not proprietary population-scale ticket-purchase data |
| Wheeling improves structure, not official draw odds | It can improve coverage efficiency without changing lottery mathematics |

## Extending the repository

To broaden the repository toward the user’s full vision of covering the smallest local drawings through large national jackpots, the next engineering steps are straightforward. Add more game definitions to the registry. Implement new source adapters for each jurisdiction. Normalize them into the same schema. Then expand the scoring pipeline with game-specific features and better backtests. The current codebase is already structured around that path.

## Documentation

The architectural and product-scope decisions are documented in [`docs/architecture.md`](docs/architecture.md).

## TL;DR

If you want to get this running quickly, use the following sequence.

| Step | Action |
| --- | --- |
| 1 | Clone the private repository |
| 2 | Install dependencies with `python3.11 -m pip install -r requirements.txt` and set `PYTHONPATH=src` |
| 3 | Run `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli sync --game megamillions --limit 80` |
| 4 | Run `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli rank --game megamillions --pool-size 10 --top 10` |
| 5 | Run `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli recommend --game megamillions --pool-size 10 --ticket-count 5` |
| 6 | Use `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli wheel` when you already have a preferred number pool |
| 7 | Add new adapters and game definitions to expand toward more local and state lotteries |

## References

[1]: https://arxiv.org/abs/2101.04242 "Maximizing the Expected Value of a Lottery Ticket: How to Sell and When to Buy"
[2]: https://web.williams.edu/Economics/wp/mathesonlottery.pdf "In Search of a Fair Bet in the Lottery"
[3]: https://www.cambridge.org/core/journals/judgment-and-decision-making/article/number-preferences-in-lotteries/47BA27051627CEED421AD3AEE255521E "Number preferences in lotteries"
[4]: https://lottoexpert.net/picking-winning-numbers/lottery-wheeling-systems "Lottery Wheeling Systems | Structured Coverage Explained Clearly"
[5]: https://www.powerball.com/previous-results "Previous Results | Powerball"
[6]: https://www.megamillions.com/winning-numbers/previous-drawings.aspx "Previous Drawings | Mega Millions"
[7]: https://nclottery.com/powerball-past-draws "Powerball - Past Draws | NC Education Lottery"
[8]: https://catalog.data.gov/dataset/lottery-mega-millions-winning-numbers-beginning-2002 "Lottery Mega Millions Winning Numbers: Beginning 2002"
