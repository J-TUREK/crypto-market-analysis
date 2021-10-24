import binance
import pandas as pd
import numpy as np
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


def relative_magnitude(x, lookback=100):
    return (sum(x < x.iloc[-1]) / lookback) * 100


def rolling_count(val):
    if val == rolling_count.previous:
        rolling_count.count += 1
    else:
        rolling_count.previous = val
        rolling_count.count = 1
    return rolling_count.count


rolling_count.count = 0  # static variable
rolling_count.previous = None  # static variable


def get_connors_rsi(df: pd.DataFrame) -> pd.DataFrame:

    # Connor's RSI
    # CRSI (3, 2, 100) = [ RSI (3 periods) + RSI Up/Down Length (2 periods) + ROC (100) ] / 3

    # Calculate RSI 3-period
    delta = df['close'].diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)

    ema_rsi_up = up.ewm(com=2, adjust=False).mean()
    ema_rsi_down = down.ewm(com=2, adjust=False).mean()
    rs_rsi = ema_rsi_up/ema_rsi_down  # Relative strength

    df['RSI-3'] = 100 - (100/(1 + rs_rsi))  # RSI
    df['RSI-3'].iloc[:3] = np.nan  # Invalid first 3 elements

    df['streak'] = df['close'] > df['close'].shift()
    df['streak-count'] = df['streak'].apply(rolling_count)
    df.loc[
        df['streak'] == False,
        'streak-count'] = df.loc[df['streak'] == False, 'streak-count'] * -1

    delta = df['streak-count'].diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)

    ema_streak_up = up.ewm(com=2, adjust=False).mean()
    ema_streak_down = down.ewm(com=2, adjust=False).mean()
    rs = ema_streak_up/ema_streak_down  # Relative strength

    df['streak-RSI'] = 100 - (100/(1 + rs))  # RSI
    df['streak-RSI'].iloc[:3] = np.nan  # Invalid first 14 elements

    prev_close = df['close'].shift()
    df['return-1'] = ((df['close'] - prev_close) / prev_close) * 100

    df['relative-magnitude'] = df['return-1'].rolling(
        100).apply(relative_magnitude)

    df['CRSI'] = (df['RSI-3'] + df['streak-RSI'] +
                  df['relative-magnitude']) / 3

    return df


def get_rsi_average(df: pd.DataFrame) -> pd.DataFrame:
    '''Returns Spark's first custom technical indicator'''

    df['spark1'] = (df['RSI'] + df['CRSI'] + df['stochRSI'])/3

    return df
