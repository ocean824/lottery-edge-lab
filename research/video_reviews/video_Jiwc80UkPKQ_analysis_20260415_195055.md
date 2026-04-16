Empirically Grounded
- Lottery draws are fundamentally random events designed with complex algorithms, random number generators (RNG), and physical ball machines to ensure unpredictability.
- The Gambler's Fallacy: The belief that past lottery results can help predict future results is statistically false. The odds of a specific number sequence being drawn remain the exact same for every draw, regardless of past outcomes.
- Machine learning models cannot accurately predict the next sequence in a truly random system.
- Statistically, there is no difference in the odds of winning whether a player continuously plays the exact same set of numbers or picks a new set for every draw.

Heuristic but Codeable
- Linear Regression: Using basic predictive analysis to guess the next number based on a small sequence of previous numbers.
- Long Short-Term Memory (LSTM): Implementing a type of Recurrent Neural Network (RNN) to analyze historical sequential data and attempt to find complex patterns.
- High-Number Bias Strategy: Selecting numbers higher than 31. Since many players use calendar dates (1-31) for their picks, choosing higher numbers doesn't increase the odds of winning, but it decreases the statistical likelihood of having to split the jackpot with others if those numbers do win.
- Static Number Persistence: A behavioral heuristic (based on an anecdotal claim from a 20-year player) of playing the exact same set of numbers consistently over a long period under the assumption that they are eventually "bound to hit."
- Automated Data Parsing: Downloading historical draw data as a CSV file and coding a script to extract specific columns (e.g., columns E through K) to feed into a predictive model.

Marketing Claims
- Claims of "hitting the jackpot" and "predicting the unpredictable" are used as initial hooks to build excitement, though the creator later debunks the feasibility of actually doing this.
- Framing AI and ChatGPT as tools to "crack the code" of the lottery.

Implementation Ideas
- Python Scripting: Use Python to build the predictive models and handle data processing.
- CSV Integration: Instead of manually inputting small strings of numbers, download decades of historical lottery data (e.g., 2010-2023) in CSV format and write a script to parse the relevant columns into an array for training.
- Advanced ML Libraries: Utilize comprehensive machine learning libraries such as TensorFlow, PyTorch, Keras, Scikit-learn, XGBoost, LightGBM, or CatBoost to build more sophisticated models.
- Domain Pivoting: Since the lottery is completely random, take the exact same LSTM or ML implementation ideas and apply them to systems that are influenced by actual variables and are not entirely random, such as stock market prices or sports betting.