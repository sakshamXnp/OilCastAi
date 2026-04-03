import sys
import os
import logging

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal, engine
from database import models
from data_pipeline.ingestion import DataOrchestrator
from ml_models.training.manager import ModelManager
from scripts.seed_commodities import seed_commodities

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_sync():
    db = SessionLocal()
    try:
        logger.info("Step 1: Seeding all 140+ commodities...")
        seed_commodities(db)
        
        logger.info("Step 2: Starting Deep Sync (365 days of benchmark data)...")
        orchestrator = DataOrchestrator(db)
        orchestrator.update_all_data(days=365)
        
        logger.info("Step 3: Starting High-Accuracy LSTM Training & Propagation...")
        model_manager = ModelManager(db)
        model_manager.train_all()
        
        logger.info("!!! TOTAL PLATFORM POPULATION COMPLETE !!!")
        logger.info("You can now refresh your dashboard.")
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    force_sync()
