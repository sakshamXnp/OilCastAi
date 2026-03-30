import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.models import Commodity, PriceData, EconomicIndicator
from .yf_source import YFinanceSource
from .sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)

# Yahoo Finance tickers that can be auto-fetched
YF_TICKERS = {
    # Futures & Indexes
    "CL=F", "BZ=F", "NG=F", "RB=F", "HO=F", "GC=F",
    "DCB=F", "MURBN.ME", "OP=F", "CCI=F",
    
    # We'll also allow the literal string names if we added them to the seed list to be queried from YF
    # Note: Yahoo Finance has limited coverage for physical spot blends. Wait until a user hooks up a Bloomberg/S&P Global API.
}

class DataOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.sources = [YFinanceSource()]
        self.sentiment_analyzer = SentimentAnalyzer()
        # Economic Symbols mapping: Name -> YFinance Ticker
        self.ECON_SYMBOLS = {
            "USD Index": "DX-Y.NYB",
            "S&P 500 VIX": "^VIX",
            "Oil Volatility Index": "^OVX",
            "Gold": "GC=F"
        }

    def run(self, days: int = 365):
        """Standard entry point for the orchestrator."""
        self.update_all_data(days=days)

    def update_all_data(self, days: int = 365):
        """Update historical prices and economic indicators."""
        # 1. Update Commodities (only those with YFinance tickers)
        commodities = self.db.query(Commodity).all()
        for commodity in commodities:
            if commodity.symbol not in YF_TICKERS:
                continue
            logger.info(f"Processing updates for {commodity.name}...")
            for source in self.sources:
                df = source.fetch(commodity, days=days)
                if df.empty:
                    continue
                self._store_prices(commodity, df, source.__class__.__name__.replace("Source", "").lower())
        
        # 2. Update Economic Indicators
        for name, ticker in self.ECON_SYMBOLS.items():
            logger.info(f"Processing updates for Economic Indicator: {name}...")
            source = self.sources[0]  # YFinance
            df = source.fetch(ticker, days=days)
            if not df.empty:
                self._store_economic_indicators(name, df, "yfinance")

        # 3. News Sentiment Analysis
        self.sentiment_analyzer.fetch_and_analyze_news(self.db)

    def _store_prices(self, commodity, df, source_name):
        """Store price data using SQLite-compatible upsert."""
        stored = 0
        skipped = 0
        
        for _, row in df.iterrows():
            price = float(row['price'])
            timestamp = row['timestamp']
            
            # Check if record already exists
            existing = self.db.query(PriceData).filter(
                PriceData.commodity_id == commodity.id,
                PriceData.timestamp == timestamp
            ).first()
            
            if existing:
                if existing.price != price:
                    existing.price = price
                    stored += 1
                else:
                    skipped += 1
            else:
                self.db.add(PriceData(
                    commodity_id=commodity.id,
                    price=price,
                    timestamp=timestamp,
                    source=source_name
                ))
                stored += 1
        
        try:
            self.db.commit()
            logger.info(f"Updated {stored} price records for {commodity.name} (skipped {skipped} unchanged)")
        except Exception as e:
            logger.error(f"Failed to store prices for {commodity.name}: {e}")
            self.db.rollback()

    def _store_economic_indicators(self, name, df, source_name):
        """Store economic indicator data using SQLite-compatible upsert."""
        stored = 0
        skipped = 0
        
        for _, row in df.iterrows():
            value = float(row['price'])
            timestamp = row['timestamp']
            
            existing = self.db.query(EconomicIndicator).filter(
                EconomicIndicator.indicator_name == name,
                EconomicIndicator.timestamp == timestamp
            ).first()
            
            if existing:
                if existing.value != value:
                    existing.value = value
                    stored += 1
                else:
                    skipped += 1
            else:
                self.db.add(EconomicIndicator(
                    indicator_name=name,
                    value=value,
                    timestamp=timestamp,
                    source=source_name
                ))
                stored += 1
        
        try:
            self.db.commit()
            logger.info(f"Updated {stored} records for indicator: {name} (skipped {skipped} unchanged)")
        except Exception as e:
            logger.error(f"Failed to store economic indicator {name}: {e}")
            self.db.rollback()

def fetch_and_store_oil_data(db: Session):
    """Legacy wrapper for backward compatibility."""
    orchestrator = DataOrchestrator(db)
    orchestrator.update_all_data()
