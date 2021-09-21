import binance
import pandas as pd
import math
import pytz
import time
import ast
import matplotlib.pyplot as plt


def clean_ohlc_csv(file_name):

    df = pd.read_csv(file_name)

    # Convert to OHLC table
    OHLC = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    not_ohlc = [x for x in df.columns if x not in OHLC]

    df.drop(columns=not_ohlc, inplace=True)  # Drop columns which are not OHLC
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.rename(columns={"timestamp": "datetime"}, inplace=True)
    df = df.set_index('datetime')

    return df


def technical_indicators(df: pd.DataFrame):

    df['MA20'] = df['close'].rolling(20).mean()  # Moving average, 20 periods
    df['MA7'] = df['close'].rolling(7).mean()  # Moving average, 7 periods
    df['TP'] = (df['close'] + df['low'] + df['high'])/3  # Technical price TBC
    # Standard deviation from technical price
    df['std'] = df['TP'].rolling(20).std(ddof=0)
    # Rolling 20 period TP used to calculate Bollinger bands
    df['MA-TP'] = df['TP'].rolling(20).mean()
    # Upper Bollinger band, 20 periods
    df['BOLU20'] = df['MA-TP'] + 2*df['std']
    # Lower Bollinger band, 20 periods
    df['BOLD20'] = df['MA-TP'] - 2*df['std']
    df['EMA12'] = df['close'].ewm(
        span=12, adjust=False).mean()  # EMA, 12 periods for MACD
    df['EMA20'] = df['close'].ewm(
        span=20, adjust=False).mean()  # EMA, 20 periods
    df['EMA26'] = df['close'].ewm(
        span=26, adjust=False).mean()  # EMA, 26 periods for MACD
    df['EMA50'] = df['close'].ewm(
        span=50, adjust=False).mean()  # EMA, 50 periods
    df['EMA100'] = df['close'].ewm(
        span=100, adjust=False).mean()  # EMA, 100 periods
    # MACD, Moving Average Convergence Divergence
    df['MACD'] = df['EMA12'] - df['EMA26']

    # RSI calculation
    delta = df['close'].diff()
    df['delta'] = delta  # Difference between current and previous close
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up/ema_down  # Relative strength

    df['RSI'] = 100 - (100/(1 + rs))  # RSI
    df['RSI'].iloc[:14] = np.nan  # Invalid first 14 elements

    # Stochastic RSI
    df['14-RSI-high'] = df['RSI'].rolling(14).max()
    df['14-RSI-low'] = df['RSI'].rolling(14).min()
    df['stochRSI'] = (df['RSI'] - df['14-RSI-low']) / \
        (df['14-RSI-high'] - df['14-RSI-low'])

    # Stochastic oscillator calculation
    df['14-high'] = df['high'].rolling(14).max()
    df['14-low'] = df['low'].rolling(14).min()
    df['%K'] = (df['close'] - df['14-low'])*100/(df['14-high'] -
                                                 df['14-low'])  # "Fast" Stochastic indicator
    df['%D'] = df['%K'].rolling(3).mean()  # "Slow" Stochastic indicator

    return df
