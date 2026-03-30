from database.database import SessionLocal
from database.models import Commodity
import json

def final_audit():
    db = SessionLocal()
    try:
        commodities = db.query(Commodity).all()
        res = [{"name": c.name, "symbol": c.symbol} for c in commodities]
        print(json.dumps(res, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    final_audit()
