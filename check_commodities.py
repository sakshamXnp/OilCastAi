from database.database import SessionLocal
from database.models import Commodity, PriceData
import json

def check():
    db = SessionLocal()
    try:
        commodities = db.query(Commodity).all()
        res = []
        for c in commodities:
            latest = db.query(PriceData).filter_by(commodity_id=c.id).order_by(PriceData.timestamp.desc()).first()
            res.append({
                "id": c.id,
                "name": c.name,
                "symbol": c.symbol,
                "latest_price": float(latest.price) if latest else None,
                "latest_timestamp": str(latest.timestamp) if latest else None
            })
        print(json.dumps(res, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    check()
