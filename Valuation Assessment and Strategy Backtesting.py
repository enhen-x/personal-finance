import yfinance as yf
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 使用微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 验证字体是否正确加载
print("当前字体：", plt.rcParams['font.sans-serif'])

def backtest_tsla(start_date="2020-01-01", end_date="2025-04-07", 
                  sma_short=50, sma_long=200, rsi_period=14):
    # 1. 获取数据
    df = yf.download("TSLA", start=start_date, end=end_date)
    df.dropna(inplace=True)
    
    # 确保 'Close' 是一维的 Series
    close_series = df['Close'].squeeze()  # 将 Close 列转换为一维序列
    
    # 2. 计算技术指标
    df['SMA_short'] = close_series.rolling(window=sma_short).mean()
    df['SMA_long']  = close_series.rolling(window=sma_long).mean()
    df['RSI']       = ta.momentum.RSIIndicator(close_series, window=rsi_period).rsi()
    macd = ta.trend.MACD(close_series)
    df['MACD']        = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    
    # # 添加调试信息
    # print("Close 列的类型:", type(close_series))
    # print("Close 列的形状:", close_series.shape)
    
    # 3. 生成信号：1=持仓，0=空仓
    df['signal'] = 0
    # 满足多头条件：短均线在长均线上方，RSI<70，MACD线上穿Signal
    long_cond = (
        (df['SMA_short'] > df['SMA_long']) &
        (df['RSI'] < 70) &
        (df['MACD'] > df['MACD_signal'])
    )
    # 空头条件：短均线跌破长均线，RSI>70，MACD线下穿Signal
    short_cond = (
        (df['SMA_short'] < df['SMA_long']) &
        (df['RSI'] > 70) &
        (df['MACD'] < df['MACD_signal'])
    )
    df.loc[long_cond,  'signal'] = 1
    df.loc[short_cond, 'signal'] = 0
    # 信号向前填充，表示持仓状态
    df['position'] = df['signal'].shift(1).fillna(0)
    
    # 4. 计算策略收益
    df['market_ret']   = df['Close'].pct_change()
    df['strategy_ret'] = df['market_ret'] * df['position']
    df.dropna(inplace=True)
    
    # 5. 累计收益曲线
    df['cum_market']   = (1 + df['market_ret']).cumprod() - 1
    df['cum_strategy'] = (1 + df['strategy_ret']).cumprod() - 1
    
    # 6. 绩效指标
    total_days = (df.index[-1] - df.index[0]).days
    years = total_days / 365.25
    strat_final = df['cum_strategy'].iloc[-1]
    bh_final    = df['cum_market'].iloc[-1]
    cagr_strat = (1 + strat_final)**(1/years) - 1
    cagr_bh    = (1 + bh_final)**(1/years) - 1
    

    
    # 7.输出结果
    print(f"回测期间：{start_date} 至 {end_date}")
    print(f"策略累计收益：{strat_final:.2%}，年化收益 (CAGR)：{cagr_strat:.2%}")
    print(f"买入持有累计：{bh_final:.2%}，年化收益 (CAGR)：{cagr_bh:.2%}")
    print(f"总交易次数：{(df['signal'].diff() != 0).sum()} 次")

    # 8. 绘图
    plt.figure(figsize=(12,5))
    plt.plot(df['cum_market'],   label="Buy & Hold")
    plt.plot(df['cum_strategy'], label="Strategy")
    plt.title("TSLA 累计收益对比")
    plt.xlabel("Date"); plt.ylabel("Cumulative Return")
    plt.legend(); plt.grid(True)
    plt.show()
    return df

# 运行回测
df_res = backtest_tsla()
