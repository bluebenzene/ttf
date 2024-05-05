import ccxt
import pandas as pd

# Set up the exchange
exchange = ccxt.binance({
    'enableRateLimit': True
})

# Parameters for data fetching
symbol = 'LTC/USDT'
timeframe = '15m'  # 15-minute intervals
# Ensure sufficient historical data
since = exchange.parse8601('2024-04-24T00:00:00Z')
limit = 2500  # Increased limit

# Fetch the data
data = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
df.set_index('Timestamp', inplace=True)

# Parameters for TTF calculation
length = 15

# Helper function to shift the data
def prev(df, periods):
    return df.shift(periods)

# Calculate TTF
def calc_ttf(df, periods):
    highest_high = df['High'].rolling(window=periods).max()
    lowest_low = df['Low'].rolling(window=periods).min()
    bp = highest_high - prev(lowest_low, periods)
    sp = prev(highest_high, periods) - lowest_low
    if (bp + sp).eq(0).any():
        print("Zero division error potential where bp + sp = 0")
    ttf = 100 * (bp - sp) / (0.5 * (bp + sp))
    return ttf

# Applying the TTF calculation
df['TTF'] = calc_ttf(df, length)

# Round the TTF values to 2 decimal places and ensure all numeric columns are formatted
df = df.round({'Open': 2, 'High': 2, 'Low': 2, 'Close': 2, 'TTF': 2})

# Display the DataFrame
print(df[['Open', 'High', 'Low', 'Close', 'TTF']].tail(10))
