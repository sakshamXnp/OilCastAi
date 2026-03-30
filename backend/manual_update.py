import platform
from collections import namedtuple
_uname_res = namedtuple('uname_result', ['system', 'node', 'release', 'version', 'machine', 'processor'])
platform.uname = lambda: _uname_res('Windows', 'Node', '10', '10.0', 'AMD64', 'AMD64')

import logging
logging.basicConfig(level=logging.INFO)

from database import database
from data_pipeline.ingestion import DataOrchestrator

def run_update():
    db = database.SessionLocal()
    try:
        orchestrator = DataOrchestrator(db)
        print("Starting manual update for all commodities...")
        orchestrator.update_all_data()
        print("Manual update completed.")
    except Exception as e:
        print(f"Error during update: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_update()
