import yfinance as yf
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt

# …（省略之前的 backtest_tsla 函数）…

def current_decision(symbol="TSLA",
                     initial_capital=100000,
                     sma_short=50,
                     sma_long=200,
                     rsi_period=14):
    """
    实时决策函数：
    - 根据最新的 SMA、MACD、RSI 三指标给出买入/卖出/观望信号
    - 根据 initial_capital 和 最新收盘价 计算建议交易数量（整股）
    """
    # 1. 拉取最近一年的日线数据
    df = yf.download(symbol, period="3y", auto_adjust=True)
    df.dropna(inplace=True)

    close = df['Close'].squeeze()

    # 2. 计算技术指标
    sma_short_s = close.rolling(window=sma_short).mean()
    sma_long_s  = close.rolling(window=sma_long).mean()
    rsi_s       = ta.momentum.RSIIndicator(close, window=rsi_period).rsi()
    macd_obj    = ta.trend.MACD(close)
    macd_s      = macd_obj.macd()
    macd_sig_s  = macd_obj.macd_signal()

    # 3. 获取最新值
    last_price       = close.iloc[-1]
    last_sma_short   = sma_short_s.iloc[-1]
    last_sma_long    = sma_long_s.iloc[-1]
    last_rsi         = rsi_s.iloc[-1]
    last_macd        = macd_s.iloc[-1]
    last_macd_signal = macd_sig_s.iloc[-1]

    # 4. 判断信号
    if (last_sma_short > last_sma_long) and (last_rsi < 70) and (last_macd > last_macd_signal):
        action = "买入"
        quantity = int(initial_capital // last_price)
    elif (last_sma_short < last_sma_long) and (last_rsi > 70) and (last_macd < last_macd_signal):
        action = "卖出"
        # 假设当前持仓 = initial_capital // last_price
        quantity = int(initial_capital // last_price)
    else:
        action = "观望"
        quantity = 0

    # 5. 输出结果
    print(f"标的：{symbol}")
    print(f"当前价格：{last_price:.2f} USD")
    print(f"最新 SMA50：{last_sma_short:.2f}, SMA200：{last_sma_long:.2f}")
    print(f"最新 RSI：{last_rsi:.2f}")
    print(f"最新 MACD：{last_macd:.4f}, Signal：{last_macd_signal:.4f}")
    print(f"决策信号：{action}")
    print(f"建议交易数量：{quantity} 股（基于初始资金 {initial_capital} USD）")

    return action, quantity

# 调用示例
if __name__ == "__main__":
    # 先运行回测（可选）
    # df_res = backtest_tsla()

    # 再看当前决策
    current_decision()
