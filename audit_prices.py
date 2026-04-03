import platform, json
from collections import namedtuple
_uname_res = namedtuple('uname_result', ['system', 'node', 'release', 'version', 'machine', 'processor'])
platform.uname = lambda: _uname_res('Windows', 'Node', '10', '10.0', 'AMD64', 'AMD64')

from database import database, models

def audit():
    db = database.SessionLocal()
    try:
        res = []
        comms = db.query(models.Commodity).all()
        for c in comms:
            latest = db.query(models.PriceData).filter_by(commodity_id=c.id).order_by(models.PriceData.timestamp.desc()).first()
            res.append({
                'name': c.name,
                'symbol': c.symbol,
                'cat': c.category,
                'price': float(latest.price) if latest else None,
                'count': db.query(models.PriceData).filter_by(commodity_id=c.id).count()
            })
        print(json.dumps(res, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    audit()
