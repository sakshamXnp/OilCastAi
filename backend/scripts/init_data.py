import logging
from database.database import SessionLocal
from data_pipeline.ingestion import DataOrchestrator
from ml_models.training.manager import ModelManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing Energy Intelligence Platform Data Pipeline...")
    
    db = SessionLocal()
    try:
        # 1. Ingest Multi-Commodity Data
        logger.info("Step 1: Orchestrating data ingestion for all benchmarks...")
        orchestrator = DataOrchestrator(db)
        orchestrator.run()
        logger.info("Data ingestion phase complete.")
        
        # 2. Initial Model Training
        logger.info("Step 2: Starting global model training suite (LSTM, Arima, LR)...")
        manager = ModelManager(db)
        manager.train_all()
        logger.info("Platform initialization successful. All models and benchmarks are live.")
        
    except Exception as e:
        logger.error(f"Platform initialization failed: {str(e)}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    main()
