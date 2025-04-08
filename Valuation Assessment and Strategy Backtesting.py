import yfinance as yf
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams

# Set default font (if needed for multilingual display)
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False  # Fix minus sign display

# Confirm font loaded
print("Current font:", plt.rcParams['font.sans-serif'])

def backtest_tsla(start_date="2020-01-01", end_date="2025-04-07", 
                  sma_short=50, sma_long=200, rsi_period=14):
    # 1. Fetch data
    df = yf.download("TSLA", start=start_date, end=end_date)
    df.dropna(inplace=True)

    # Ensure 'Close' is a 1D Series
    close_series = df['Close'].squeeze()
    
    # 2. Calculate technical indicators
    df['SMA_short'] = close_series.rolling(window=sma_short).mean()
    df['SMA_long']  = close_series.rolling(window=sma_long).mean()
    df['RSI']       = ta.momentum.RSIIndicator(close_series, window=rsi_period).rsi()
    macd = ta.trend.MACD(close_series)
    df['MACD']        = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    
    # 3. Generate signals: 1 = long, 0 = cash
    df['signal'] = 0
    # Long condition: short MA > long MA, RSI < 70, MACD > signal
    long_cond = (
        (df['SMA_short'] > df['SMA_long']) &
        (df['RSI'] < 70) &
        (df['MACD'] > df['MACD_signal'])
    )
    # Short condition: short MA < long MA, RSI > 70, MACD < signal
    short_cond = (
        (df['SMA_short'] < df['SMA_long']) &
        (df['RSI'] > 70) &
        (df['MACD'] < df['MACD_signal'])
    )
    df.loc[long_cond,  'signal'] = 1
    df.loc[short_cond, 'signal'] = 0
    # Forward fill signals to represent position holding
    df['position'] = df['signal'].shift(1).fillna(0)
    
    # 4. Calculate returns
    df['market_ret']   = df['Close'].pct_change()
    df['strategy_ret'] = df['market_ret'] * df['position']
    df.dropna(inplace=True)
    
    # 5. Cumulative return curves
    df['cum_market']   = (1 + df['market_ret']).cumprod() - 1
    df['cum_strategy'] = (1 + df['strategy_ret']).cumprod() - 1
    
    # 6. Performance metrics
    total_days = (df.index[-1] - df.index[0]).days
    years = total_days / 365.25
    strat_final = df['cum_strategy'].iloc[-1]
    bh_final    = df['cum_market'].iloc[-1]
    cagr_strat = (1 + strat_final)**(1/years) - 1
    cagr_bh    = (1 + bh_final)**(1/years) - 1

    # 7. Output results
    print(f"Backtest period: {start_date} to {end_date}")
    print(f"Strategy cumulative return: {strat_final:.2%}, CAGR: {cagr_strat:.2%}")
    print(f"Buy & Hold cumulative return: {bh_final:.2%}, CAGR: {cagr_bh:.2%}")
    print(f"Total number of trades: {(df['signal'].diff() != 0).sum()}")

    # 8. Plot
    plt.figure(figsize=(12,5))
    plt.plot(df['cum_market'],   label="Buy & Hold")
    plt.plot(df['cum_strategy'], label="Strategy")
    plt.title("TSLA Cumulative Return Comparison")
    plt.xlabel("Date"); plt.ylabel("Cumulative Return")
    plt.legend(); plt.grid(True)
    plt.show()
    
    return df

# Run backtest
df_res = backtest_tsla()
