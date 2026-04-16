Here is a summary of the lottery strategies, formulas, claims, and codeable heuristics discussed in the video, categorized as requested:

Empirically Grounded
- The core mechanism involves randomly generating 5 distinct numbers from a pool of 1 to 69.
- Any given combination of numbers will possess basic statistical properties, such as a total sum, a ratio of odd to even numbers, and a distribution across the lower and upper halves of the number pool.

Heuristic but Codeable
- Sum Range: Filtering generated combinations to ensure the sum of the 5 numbers falls within a specific target range (e.g., between 150 and 200).
- Parity Ratio: Restricting combinations to a specific balance of odd and even numbers, such as requiring exactly 3 odd and 2 even numbers, or 2 odd and 3 even numbers.
- High/Low Balance: Enforcing a distribution where a combination must contain at least a certain number of "low" numbers (1-34) and "high" numbers (35-69), for example, at least 2 of each.
- Arithmetic Complexity (AC): A calculated metric based on the number of unique differences between all possible pairs of numbers in a draw. The strategy involves filtering for combinations that match a frequently occurring AC value (e.g., an AC of 8 or 9).

Marketing Claims
- Most people use AI incorrectly for lotteries; directly asking AI tools to predict winning numbers results in "made up" answers because AI designers have implemented safeguards against this.
- You can bypass AI safety filters and detection of sensitive terms like "lottery" by framing the historical data as a "complex math game."
- Constraining random number generation within these specific heuristic ranges "greatly increases the probability of hitting the target."
- Asking the AI to only analyze the 5 main numbers (white balls) and ignoring the special number (red ball) helps prevent the AI from realizing it is calculating lottery tickets.

Implementation Ideas
- Data Preparation: Create a spreadsheet containing recent historical draws (e.g., the last 20) and pre-calculate metrics like the Sum, Parity ratio, and AC value for each draw.
- Prompt Engineering: Upload the spreadsheet to an AI and ask it to analyze the rules and patterns of this "math game" to extract target ranges for the metrics.
- Script Generation: Instruct the AI to write a program (such as a Python script).
- Constraint Loop: The script should use a loop to continuously generate random 5-number combinations, calculate the Sum, Parity, High/Low, and AC for each, and only output the combinations that meet all the defined heuristic constraints.