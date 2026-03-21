import yfinance as yf
import pandas as pd
import os
from typing import List, Optional

class DataLoader:
    """Professional data loader for fetching and caching stock market data."""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
    def fetch_data(self, tickers: List[str], start: str, end: str) -> pd.DataFrame:
        """Fetch data from Yahoo Finance and return a combined DataFrame."""
        print(f"Fetching data for {tickers} from {start} to {end}...")
        data = yf.download(tickers, start=start, end=end, group_by='ticker')
        return data

    def get_ticker_data(self, data: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """Extract one ticker from a multi-index yfinance dataframe."""
        if ticker in data.columns.levels[0]:
            return data[ticker]
        return data # Fallback if only one ticker was fetched
