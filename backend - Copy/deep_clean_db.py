from database.database import SessionLocal
from database.models import Commodity, PriceData
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deep_clean():
    db = SessionLocal()
    try:
        commodities = db.query(Commodity).all()
        for c in commodities:
            # Full cleanup of name and symbol
            new_name = c.name.split('\n')[0].strip()
            if "HORSE" in new_name:
                new_name = new_name.replace("HORSE", "").strip()
            
            if c.name != new_name:
                logger.info(f"Renaming '{c.name}' to '{new_name}'")
                c.name = new_name
            
            # Ensure symbols are clean too
            if c.symbol:
                new_symbol = c.symbol.strip()
                if c.symbol != new_symbol:
                    logger.info(f"Cleaning symbol '{c.symbol}' to '{new_symbol}'")
                    c.symbol = new_symbol

        db.commit()
        logger.info("Deep clean completed.")
    except Exception as e:
        logger.error(f"Clean failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    deep_clean()
