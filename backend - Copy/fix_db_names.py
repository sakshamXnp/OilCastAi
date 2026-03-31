from database.database import SessionLocal
from database.models import Commodity, PriceData
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_data():
    db = SessionLocal()
    try:
        # 1. Fix malformed commodity names
        comms = db.query(Commodity).all()
        for c in comms:
            original_name = c.name
            clean_name = c.name.split('\n')[0].strip()
            if "HORSE" in clean_name:
                clean_name = clean_name.replace("HORSE", "").strip()
            
            if original_name != clean_name:
                logger.info(f"Cleaning name: '{original_name}' -> '{clean_name}'")
                c.name = clean_name
        
        # 2. Update symbols to better match oilprice.com benchmarks where possible
        # BZ=F (Brent Futures) -> Brent
        # CL=F (WTI Futures) -> WTI
        # Note: yfinance primarily has futures. 
        # We will keep futures but ensure they are the most recent.
        
        # 3. Commit changes
        db.commit()
        logger.info("Database names cleaned.")
        
    except Exception as e:
        logger.error(f"Error fixing data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_data()
