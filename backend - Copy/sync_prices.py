import logging
from database.database import SessionLocal
from database.models import Commodity, PriceData
from data_pipeline.ingestion import DataOrchestrator
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Best matching tickers for oilprice.com benchmarks
TICKER_MAP = {
    "Brent Crude": "BZ=F",
    "WTI Crude": "CL=F",
    "Natural Gas": "NG=F",
    "Gasoline": "RB=F",
    "Heating Oil": "HO=F",
    "Dubai": "DCB=F", # Dubai Crude (Platts) Futures
    "Murban": "MURBN.ME", # Murban Crude Oil Futures
}

def sync():
    db = SessionLocal()
    try:
        # 1. Ensure commodities have the best known tickers
        logger.info("Synchronizing commodity symbols...")
        commodities = db.query(Commodity).all()
        for c in commodities:
            name = c.name
            if name in TICKER_MAP:
                if c.symbol != TICKER_MAP[name]:
                    logger.info(f"Updating symbol for {name}: {c.symbol} -> {TICKER_MAP[name]}")
                    c.symbol = TICKER_MAP[name]
        
        db.commit()
        
        # 2. Trigger orchestrator for full refresh (last 7 days to ensure overlap and accuracy)
        logger.info("Starting data refresh orchestrator...")
        orchestrator = DataOrchestrator(db)
        orchestrator.update_all_data(days=7)
        
        logger.info("Price synchronization and refresh completed.")
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync()
