import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
import argparse
import os

# === Command line argument for base file name ===
parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, default='hidden_gems_watchlist.csv', help='Base filename for output')
args = parser.parse_args()

base_filename = args.file

# === Step 1: Define your stock universe ===
tickers = ['ZNGA', 'NIO', 'PLUG', 'FUBO', 'RBLX', 'AFRM']  # replace with full list

# === Step 2: Fetch historical data ===
data_dict = {}
for ticker in tickers:
    df = yf.download(ticker, period='6mo', interval='1d', progress=False)
    if df.empty:
        continue
    data_dict[ticker] = df

# === Step 3: Calculate technical indicators and fundamentals ===
results = []
for ticker, df in data_dict.items():
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    df['MACD'] = ta.trend.MACD(df['Close']).macd_diff()
    last_close = df['Close'].iloc[-1]
    rsi = df['RSI'].iloc[-1]
    macd_diff = df['MACD'].iloc[-1]
    
    # Fetch fundamental info
    info = yf.Ticker(ticker).info
    market_cap = info.get('marketCap', 0)
    avg_volume = info.get('averageVolume', 0)
    earnings_growth = info.get('earningsQuarterlyGrowth', 0)
    analyst_coverage = len(info.get('recommendationMean', [])) if info.get('recommendationMean') else 0
    
    # Scoring: simple example
    score = 0
    score += 5 if 30 < rsi < 50 else 0  # oversold/moderate
    score += 5 if macd_diff > 0 else 0  # bullish momentum
    score += 5 if market_cap < 2e9 else 0  # small-cap bonus
    score += 5 if earnings_growth and earnings_growth > 0 else 0
    score += 5 if analyst_coverage < 5 else 0  # low coverage
    
    results.append({
        'Ticker': ticker,
        'LastClose': last_close,
        'RSI': rsi,
        'MACD_Diff': macd_diff,
        'MarketCap': market_cap,
        'AvgVolume': avg_volume,
        'EarningsGrowth': earnings_growth,
        'Score': score
    })

# === Step 4: Create DataFrame and sort ===
watchlist = pd.DataFrame(results)
watchlist.sort_values(by='Score', ascending=False, inplace=True)

# === Step 5: Save files ===
today_str = datetime.now().strftime('%Y-%m-%d')

# 1️⃣ Dated file in repo
dated_file = f"hidden_gems_watchlist_{today_str}.csv"
watchlist.to_csv(dated_file, index=False)

# 2️⃣ Latest file for email
latest_file = base_filename.replace('.csv', '_latest.csv')
watchlist.to_csv(latest_file, index=False)

print(f"Watchlist saved as:\n- Dated: {dated_file}\n- Latest: {latest_file}")
