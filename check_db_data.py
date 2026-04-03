import platform
from collections import namedtuple
_uname_res = namedtuple('uname_result', ['system', 'node', 'release', 'version', 'machine', 'processor'])
platform.uname = lambda: _uname_res('Windows', 'Node', '10', '10.0', 'AMD64', 'AMD64')

from database import database, models
import json

def check_data():
    db = database.SessionLocal()
    try:
        commodities = db.query(models.Commodity).all()
        results = []
        for c in commodities:
            latest_price = db.query(models.PriceData).filter(models.PriceData.commodity_id == c.id).order_by(models.PriceData.timestamp.desc()).first()
            count = db.query(models.PriceData).filter(models.PriceData.commodity_id == c.id).count()
            results.append({
                "name": c.name,
                "symbol": c.symbol,
                "count": count,
                "latest_price": float(latest_price.price) if latest_price else None,
                "latest_date": str(latest_price.timestamp) if latest_price else None
            })
        print(json.dumps(results, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
