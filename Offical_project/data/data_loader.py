# data/data_loader.py

import os
import pandas as pd
import yfinance as yf
from typing import Tuple

DATA_DIR = "data/cache"

# ==================================================
# DOWLOAD DATA
# ==================================================
def download_price(
    symbol: str,
    start: str = "2000-01-01",
    end: str | None = None,
    auto_adjust: bool = True,
    save: bool = True
) -> pd.DataFrame:
    """
    Download historical price data from Yahoo Finance.

    Returns DataFrame with columns:
    open, high, low, close, adj_close, volume
    """

    ticker = yf.Ticker(symbol)
    df = ticker.history(
        start=start,
        end=end,
        auto_adjust=auto_adjust
    )

    if df.empty:
        raise ValueError(f"No data downloaded for {symbol}")

    # Chuẩn hóa column name
    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })

    # Yahoo auto_adjust thì Close = Adj Close
    if auto_adjust:
        df["adj_close"] = df["close"]
    else:
        df["adj_close"] = df.get("Adj Close", df["close"])

    df = df[["open", "high", "low", "close", "adj_close", "volume"]]

    if save:
        save_price(symbol, df)

    return df
# ==================================================
# Core helpers
# ==================================================

def _ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def _get_price_path(symbol: str) -> str:
    return os.path.join(DATA_DIR, f"{symbol}.csv")


# ==================================================
# Load & save single symbol
# ==================================================

def save_price(symbol: str, df: pd.DataFrame):
    """
    Save price dataframe to cache.
    Expect columns: ['open', 'high', 'low', 'close', 'volume']
    """
    _ensure_dir(DATA_DIR)
    path = _get_price_path(symbol)
    df.to_csv(path)


def load_price(symbol: str) -> pd.DataFrame:
    """
    Load cached price data for a symbol.
    """
    path = _get_price_path(symbol)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Price data for {symbol} not found")

    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return df


# ==================================================
# Pair loader
# ==================================================

def load_pair_prices(
    symbol_y: str,
    symbol_x: str,
    price_col: str = "close"
) -> Tuple[pd.Series, pd.Series]:
    """
    Load and align price series for a trading pair.
    Returns aligned (y, x).
    """
    df_y = load_price(symbol_y)
    df_x = load_price(symbol_x)

    if price_col not in df_y.columns or price_col not in df_x.columns:
        raise ValueError(f"Column `{price_col}` not found in price data")

    y = df_y[price_col]
    x = df_x[price_col]

    df = pd.concat([y, x], axis=1).dropna()
    df.columns = ["y", "x"]

    return df["y"], df["x"]


# ==================================================
# Universe loader
# ==================================================

def load_universe(
    symbols: list,
    price_col: str = "close"
) -> pd.DataFrame:
    """
    Load multiple symbols into a single dataframe.
    Columns = symbols
    """
    series_list = []

    for sym in symbols:
        df = load_price(sym)
        if price_col not in df.columns:
            raise ValueError(f"{price_col} not found for {sym}")
        series_list.append(df[price_col].rename(sym))

    df_all = pd.concat(series_list, axis=1).dropna()
    return df_all
