from database.database import SessionLocal, engine
from database.models import Base, Commodity, PriceData
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def nuclear_clean():
    db = SessionLocal()
    try:
        # 1. Update all commodities with clean names and the correct symbols
        # For Brent and WTI, we use the futures tickers but ensure they are clean.
        updates = {
            "Brent Crude": "BZ=F",
            "WTI Crude": "CL=F",
            "Natural Gas": "NG=F"
        }
        
        for name, symbol in updates.items():
            # Find any commodity that starts with the name (to catch "Brent Crude HORSE" etc.)
            comms = db.query(Commodity).filter(Commodity.name.like(f"{name}%")).all()
            for c in comms:
                logger.info(f"Nuclear cleaning '{c.name}' -> '{name}'")
                c.name = name
                c.symbol = symbol
        
        # 2. Final pass to remove any literal newlines or "HORSE" in ANY commodity
        all_comms = db.query(Commodity).all()
        for c in all_comms:
            clean_name = c.name.replace("HORSE", "").strip().split('\n')[0]
            if c.name != clean_name:
                c.name = clean_name
            if c.symbol:
                c.symbol = c.symbol.strip()

        db.commit()
        logger.info("Nuclear clean finished.")
    except Exception as e:
        logger.error(f"Nuclear clean failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    nuclear_clean()
