import yfinance as yf
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt

# ... (omitted backtest_tsla function) ...

def current_decision(symbol="TSLA",
                     initial_capital=100000,
                     sma_short=50,
                     sma_long=200,
                     rsi_period=14):
    """
    Real-time decision function:
    - Generates Buy/Sell/Hold signals based on latest SMA, MACD, RSI indicators
    - Calculates recommended shares to trade (whole shares) based on initial capital and latest close price
    """
    # 1. Fetch 3-year daily data
    df = yf.download(symbol, period="3y", auto_adjust=True)
    df.dropna(inplace=True)

    close = df['Close'].squeeze()

    # 2. Calculate technical indicators
    sma_short_s = close.rolling(window=sma_short).mean()
    sma_long_s  = close.rolling(window=sma_long).mean()
    rsi_s       = ta.momentum.RSIIndicator(close, window=rsi_period).rsi()
    macd_obj    = ta.trend.MACD(close)
    macd_s      = macd_obj.macd()
    macd_sig_s  = macd_obj.macd_signal()

    # 3. Get latest values
    last_price       = close.iloc[-1]
    last_sma_short   = sma_short_s.iloc[-1]
    last_sma_long    = sma_long_s.iloc[-1]
    last_rsi         = rsi_s.iloc[-1]
    last_macd        = macd_s.iloc[-1]
    last_macd_signal = macd_sig_s.iloc[-1]

    # 4. Determine signal
    if (last_sma_short > last_sma_long) and (last_rsi < 70) and (last_macd > last_macd_signal):
        action = "Buy"
        quantity = int(initial_capital // last_price)
    elif (last_sma_short < last_sma_long) and (last_rsi > 70) and (last_macd < last_macd_signal):
        action = "Sell"
        # Assuming current position = initial_capital // last_price
        quantity = int(initial_capital // last_price)
    else:
        action = "Hold"
        quantity = 0

    # 5. Output results
    print(f"Symbol: {symbol}")
    print(f"Current Price: {last_price:.2f} USD")
    print(f"Latest SMA50: {last_sma_short:.2f}, SMA200: {last_sma_long:.2f}")
    print(f"Latest RSI: {last_rsi:.2f}")
    print(f"Latest MACD: {last_macd:.4f}, Signal: {last_macd_signal:.4f}")
    print(f"Decision Signal: {action}")
    print(f"Recommended shares to trade: {quantity} (based on initial capital {initial_capital} USD)")

    return action, quantity

# Example usage
if __name__ == "__main__":
    # Run backtest first (optional)
    # df_res = backtest_tsla()

    # Get current decision
    current_decision()
