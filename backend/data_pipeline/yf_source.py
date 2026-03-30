import pandas as pd
import logging
from .base import BaseSource
from database.models import Commodity

logger = logging.getLogger(__name__)

class YFinanceSource(BaseSource):
    def fetch(self, target, days: int = 365) -> pd.DataFrame:
        if isinstance(target, str):
            ticker = target
            name = target
        else:
            ticker = target.symbol
            name = target.name
            
        if not ticker:
            return pd.DataFrame()
            
        try:
            import yfinance as yf
            logger.info(f"Fetching {name} ({ticker}) from yfinance...")
            data = yf.download(ticker, period=f"{days}d", interval="1d")
            
            if data.empty:
                return pd.DataFrame()
                
            df = data.reset_index()
            # Handle multi-index columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            # Filter for necessary columns
            df = df[['Date', 'Close']].rename(columns={'Date': 'timestamp', 'Close': 'price'})
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            logger.error(f"Error fetching from yfinance for {ticker}: {e}")
            return pd.DataFrame()

    def fetch_live(self, commodity: Commodity) -> float:
        ticker_sym = commodity.symbol
        if not ticker_sym:
            return 0.0
            
        try:
            import yfinance as yf
            ticker = yf.Ticker(ticker_sym)
            live_price = ticker.fast_info['lastPrice']
            return float(live_price) if live_price else 0.0
        except Exception as e:
            logger.error(f"Live fetch failed for {ticker_sym}: {e}")
            return 0.0
