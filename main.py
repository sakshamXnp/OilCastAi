import platform
from collections import namedtuple

# Monkey patch platform.uname() to avoid WMI hangs on Windows
_uname_res = namedtuple('uname_result', ['system', 'node', 'release', 'version', 'machine', 'processor'])
platform.uname = lambda: _uname_res('Windows', 'Node', '10', '10.0', 'AMD64', 'AMD64')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import database
from database.database import Base, engine
from config import settings
from api.routes import oil, model

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import threading
import time
from data_pipeline.ingestion import DataOrchestrator
from ml_models.training.manager import ModelManager
from scripts.seed_commodities import seed_commodities

app = FastAPI(
    title="Energy Intelligence Platform API",
    description="Professional Commodity Analytics & AI Prediction Engine",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def news_intelligence_service():
    """Background task to fetch news and market sentiment every 15 minutes."""
    while True:
        try:
            logger.info("Syncing latest market intelligence...")
            db = database.SessionLocal()
            orchestrator = DataOrchestrator(db)
            # Fetch latest historical data & news sentiment
            orchestrator.update_all_data(days=1) # Only fetch last 1 day for speed
            db.close()
            logger.info("Market intelligence sync complete.")
        except Exception as e:
            logger.error(f"Intelligence sync failed: {e}")
        
        # Sleep for 15 minutes
        time.sleep(900)

def model_training_service():
    """Background task to train models every 24 hours."""
    while True:
        try:
            # Wait 5 minutes after startup before first training to let data settle
            time.sleep(300)
            logger.info("Starting scheduled model retraining cycle...")
            db = database.SessionLocal()
            manager = ModelManager(db)
            manager.train_all()
            db.close()
            logger.info("Model retraining cycle completed.")
        except Exception as e:
            logger.error(f"Model training service failed: {e}")
        
        # Sleep for 24 hours
        time.sleep(86400)

@app.on_event("startup")
def startup_event():
    logger.info("Startup sequence initiated.")
    try:
        # Create tables
        logger.info(f"Connecting to database: {settings.DATABASE_URL}")
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas verified.")
        
        # Seed commodities
        seed_commodities()
        logger.info("Commodity metadata initialized.")
    except Exception as e:
        logger.error(f"DATABASE INITIALIZATION FAILED: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return

    try:
        # Start background maintenance services
        logger.info("Starting automated intelligence services...")
        
        # 1. News & Market Sentiment Service (Every 15 mins)
        intelligence_thread = threading.Thread(target=news_intelligence_service, daemon=True)
        intelligence_thread.start()
        
        # 2. Model Training Service (Every 24 hours)
        training_thread = threading.Thread(target=model_training_service, daemon=True)
        training_thread.start()
        
        logger.info("Deep intelligence services initiated.")
    except Exception as e:
        logger.error(f"BACKGROUND SERVICES FAILED: {e}")
        import traceback
        logger.error(traceback.format_exc())

# Mount routers at /api to match requested structure /api/commodities, etc.
app.include_router(oil.router, prefix="/api", tags=["Global Intelligence"])
app.include_router(model.router, prefix="/api/model", tags=["ML Engine"])

@app.get("/health")
def health_check():
    return {"status": "operational", "database": settings.DATABASE_URL}

@app.get("/debug/db")
def debug_db():
    from database.database import SessionLocal
    from database.models import Commodity, PriceData
    import os
    db = SessionLocal()
    commodities = db.query(Commodity).count()
    prices = db.query(PriceData).count()
    comms = [{"id": c.id, "symbol": c.symbol, "name": c.name} for c in db.query(Commodity).all()]
    db.close()
    return {
        "database_url": settings.DATABASE_URL,
        "cwd": os.getcwd(),
        "db_file_exists": os.path.exists("oilcast.db"),
        "db_file_size": os.path.getsize("oilcast.db") if os.path.exists("oilcast.db") else None,
        "commodities_count": commodities,
        "prices_count": prices,
        "commodities": comms
    }
