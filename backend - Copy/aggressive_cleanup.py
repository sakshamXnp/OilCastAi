import platform
from collections import namedtuple
_uname_res = namedtuple('uname_result', ['system', 'node', 'release', 'version', 'machine', 'processor'])
platform.uname = lambda: _uname_res('Windows', 'Node', '10', '10.0', 'AMD64', 'AMD64')

from database import database, models

def cleanup():
    db = database.SessionLocal()
    try:
        keep_symbols = ['BZ=F', 'CL=F', 'DCB=F', 'RB=F', 'HO=F', 'JET=F', 'NG=F']
        comms = db.query(models.Commodity).all()
        count = 0
        for c in comms:
            if c.symbol not in keep_symbols:
                print(f"Deleting {c.name} ({c.symbol})...")
                # Delete related data first
                db.query(models.PriceData).filter_by(commodity_id=c.id).delete()
                db.query(models.Prediction).filter_by(commodity_id=c.id).delete()
                db.query(models.ModelMetric).filter_by(commodity_id=c.id).delete()
                db.delete(c)
                count += 1
        db.commit()
        print(f"Cleanup complete. Deleted {count} commodities.")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup()
