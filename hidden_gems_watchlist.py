import yfinance as yf
import pandas as pd
import ta
import datetime
import os
import sys

# ==========================================================
# Helper: Fetch clean 1D Close price series safely
# ==========================================================
def fetch_close_series(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.Series:
    """Safely download a clean 1D 'Close' price series for a ticker."""
    try:
        data = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
        if data is None or data.empty or "Close" not in data:
            print(f"[WARN] No data for {ticker} — possibly delisted.")
            return pd.Series(dtype=float)
        close_series = data["Close"]
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]  # flatten
        return close_series.dropna()
    except Exception as e:
        print(f"[ERROR] Failed to fetch {ticker}: {e}")
        return pd.Series(dtype=float)

# ==========================================================
# Core: Generate hidden gems watchlist
# ==========================================================
def generate_hidden_gems_watchlist(file_base_name: str):
    # Define tickers for now (later we’ll automate discovery)
    tickers = ['NIO', 'PLUG', 'FUBO', 'RBLX', 'AFRM', 'HIMX', 'XPEV', 'SE', 'BILI', 'JMIA']

    results = []

    for ticker in tickers:
        close = fetch_close_series(ticker)
        if close.empty:
            continue

        try:
            # Compute RSI, MACD, and 20-day price change %
            rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
            macd = ta.trend.MACD(close).macd_diff().iloc[-1]
            price_change = (close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100

            results.append({
                "Ticker": ticker,
                "Last Price": round(close.iloc[-1], 2),
                "6M % Change": round(price_change, 2),
                "RSI": round(rsi, 2),
                "MACD Diff": round(macd, 4),
                "Signal": "Buy" if (rsi < 40 and macd > 0) else "Watch",
            })

            print(f"[OK] {ticker}: RSI={rsi:.2f}, MACD={macd:.4f}, Δ={price_change:.2f}%")

        except Exception as e:
            print(f"[ERROR] Indicator calculation failed for {ticker}: {e}")
            continue

    # Create DataFrame and sort by strongest signal
    df = pd.DataFrame(results).sort_values(by=["Signal", "6M % Change"], ascending=[False, False])

    # Build filenames
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    dated_file = f"{os.path.splitext(file_base_name)[0]}_{today}.csv"
    latest_file = f"{os.path.splitext(file_base_name)[0]}_latest.csv"

    # Save both copies
    df.to_csv(dated_file, index=False)
    df.to_csv(latest_file, index=False)

    print(f"\n✅ Saved: {dated_file}")
    print(f"✅ Saved: {latest_file}")
    print(f"Total tickers analyzed: {len(results)}")

# ==========================================================
# Entry point
# ==========================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hidden_gems_watchlist.py --file <file_name>")
        sys.exit(1)

    file_name = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--file" else "hidden_gems_watchlist.csv"
    generate_hidden_gems_watchlist(file_name)
