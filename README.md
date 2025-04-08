# personal-finance
This repository aims to document my personal explorations into stock market analysis and share some useful Python scripts.

1.Valuation Assessment and Strategy Backtesting.py:
This script automatically fetches data, calculates returns based on the decision model, and generates a cumulative returns curve.
Core Idea of the Decision Model:
(1)Trend First: Use SMA golden/death crosses to capture the overall trend.
(2)Momentum Confirmation: Filter out false breakouts with MACD.
(3)Risk Control: Use RSI to avoid chasing highs and panic selling.

2.Daily Buy or Sell Decision.py
This script determines whether to buy or sell on a given day based on technical indicators, and calculates the corresponding trade quantity.
The strategy used is consistent with "Valuation Assessment and Strategy Backtesting.py".
