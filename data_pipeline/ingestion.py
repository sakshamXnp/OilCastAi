import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.models import Commodity, PriceData, EconomicIndicator
from .yf_source import YFinanceSource
from .sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)

import random
from datetime import datetime, timedelta

# Yahoo Finance tickers that can be auto-fetched
YF_TICKERS = {
    # Futures & Indexes
    "CL=F", "BZ=F", "NG=F", "RB=F", "HO=F", "GC=F",
    "DCB=F", "MURBN.ME", "OP=F", "CCI=F",
}

# Benchmark and spread mappings for shadow commodities
# Category -> (Benchmark Ticker, Default Spread Range)
SHADOW_MAPPINGS = {
    "OPEC": ("BZ=F", (-1.5, 1.5)),       # OPEC blends usually track Brent
    "INTERNATIONAL": ("BZ=F", (-3.0, 3.0)), # Int'l benchmarks usually track Brent
    "CANADIAN": ("CL=F", (-18.0, -8.0)),    # Canadian heavy is significantly cheaper than WTI
    "US_BLEND": ("CL=F", (-2.5, 2.5)),      # US local blends track WTI closely
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
        """Update historical prices, economic indicators, and news."""
        # 1. Update Core Benchmarks (tickers in YF_TICKERS)
        self._update_core_benchmarks(days)
        
        # 2. Update Shadow Commodities (populate the rest of the 140+ oils)
        self._populate_shadow_data(days)
        
        # 3. Update Economic Indicators
        self._update_economic_indicators(days)

        # 4. News Sentiment Analysis
        self.sentiment_analyzer.fetch_and_analyze_news(self.db)

    def _update_core_benchmarks(self, days: int):
        """Update commodities that have direct Yahoo Finance tickers."""
        commodities = self.db.query(Commodity).filter(Commodity.symbol.in_(YF_TICKERS)).all()
        for commodity in commodities:
            logger.info(f"Syncing benchmark: {commodity.name} ({commodity.symbol})...")
            for source in self.sources:
                df = source.fetch(commodity, days=days)
                if not df.empty:
                    self._store_prices(commodity, df, source.__class__.__name__.replace("Source", "").lower())

    def _populate_shadow_data(self, days: int):
        """Populate non-ticker oils by shadowing benchmarks with a category-based spread."""
        logger.info("Populating shadow data for 100+ global oil blends...")
        
        # Get all commodities NOT in YF_TICKERS
        shadows = self.db.query(Commodity).filter(~Commodity.symbol.in_(YF_TICKERS)).all()
        
        for shadow in shadows:
            mapping = SHADOW_MAPPINGS.get(shadow.category)
            if not mapping:
                continue
            
            benchmark_symbol, (min_spread, max_spread) = mapping
            
            # Find the benchmark commodity
            benchmark = self.db.query(Commodity).filter(Commodity.symbol == benchmark_symbol).first()
            if not benchmark:
                continue
            
            # Update metadata for transparency
            shadow.tracking_benchmark = benchmark.name.split(' ')[0] # Use 'Brent' or 'WTI'
            
            # Get latest benchmark prices
            benchmark_prices = self.db.query(PriceData).filter(
                PriceData.commodity_id == benchmark.id
            ).order_by(PriceData.timestamp.desc()).limit(days).all()
            
            if not benchmark_prices:
                continue
            
            # Apply spread to create shadow price history
            stored = 0
            # Use deterministic random based on symbol to keep shadow price stable
            random_seed = sum(ord(c) for c in shadow.symbol)
            random.seed(random_seed)
            spread = random.uniform(min_spread, max_spread)
            shadow.current_spread = spread
            
            for bp in benchmark_prices:
                # Check if shadow price already exists for this timestamp
                existing = self.db.query(PriceData).filter(
                    PriceData.commodity_id == shadow.id,
                    PriceData.timestamp == bp.timestamp
                ).first()
                
                if not existing:
                    # Apply a small daily fluctuation to the spread so it's not a rigid parallel line
                    daily_noise = random.uniform(-0.1, 0.1)
                    shadow_price = max(1.0, bp.price + spread + daily_noise)
                    
                    self.db.add(PriceData(
                        commodity_id=shadow.id,
                        price=shadow_price,
                        timestamp=bp.timestamp,
                        source="shadow-engine"
                    ))
                    stored += 1
            
            if stored > 0:
                self.db.commit()
                logger.debug(f"Generated {stored} shadow points for {shadow.name} tracking {benchmark_symbol}")

    def _update_economic_indicators(self, days: int):
        """Update external economic factors needed for AI training."""
        for name, ticker in self.ECON_SYMBOLS.items():
            logger.info(f"Syncing Economic Indicator: {name} ({ticker})...")
            source = self.sources[0]
            df = source.fetch(ticker, days=days)
            if not df.empty:
                self._store_economic_indicators(name, df, "yfinance")

    def _store_prices(self, commodity, df, source_name):
        """Store price data using SQLite-compatible upsert."""
        stored = 0
        skipped = 0
        
        for _, row in df.iterrows():
            price = float(row['price'])
            timestamp = row['timestamp']
            
            existing = self.db.query(PriceData).filter(
                PriceData.commodity_id == commodity.id,
                PriceData.timestamp == timestamp
            ).first()
            
            if existing:
                if abs(existing.price - price) > 0.001:
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
            if stored > 0:
                logger.info(f"Updated {stored} records for {commodity.name} (skipped {skipped})")
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
                if abs(existing.value - value) > 0.001:
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
            if stored > 0:
                logger.info(f"Updated {stored} indicator records for {name} (skipped {skipped})")
        except Exception as e:
            logger.error(f"Failed to store economic indicator {name}: {e}")
            self.db.rollback()

def fetch_and_store_oil_data(db: Session):
    """Legacy wrapper for backward compatibility."""
    orchestrator = DataOrchestrator(db)
    orchestrator.update_all_data()
