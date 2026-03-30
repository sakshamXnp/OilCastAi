import logging
import sys
import pandas as pd
import numpy as np
from database import database
from database.models import Commodity, Prediction
from ml_models.training.manager import ModelManager

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

def verify():
    db = database.SessionLocal()
    manager = ModelManager(db)
    
    # Pick one commodity (e.g., Brent)
    brent = db.query(Commodity).filter(Commodity.symbol == 'BZ=F').first()
    if not brent:
        print("Brent (BZ=F) not found. Seeding first...")
        return
        
    print(f"--- Verifying Advanced ML for {brent.name} ---")
    
    # 1. Fetch and check Data
    print("Fetching data with features...")
    df = manager.fetch_data(brent)
    print(f"Data columns: {df.columns.tolist()}")
    print(f"Data shape: {df.shape}")
    print(f"Sample data:\n{df.tail(2)}")
    
    if len(df) < 50:
        print(f"Insufficient data: {len(df)} rows. Need 50+.")
        return

    # 2. Train and Predict XGBoost (Sample)
    from ml_models.models.xgboost_model import XGBoostModel
    xgb_model = XGBoostModel()
    
    print("\nTraining XGBoost...")
    metrics = xgb_model.train(df)
    print(f"Metrics: {metrics}")
    print(f"Explanation: {xgb_model.get_explanation()}")
    
    print("\nPredicting 30 days...")
    preds = xgb_model.predict(30)
    print(f"Predictions tail:\n{preds.tail(2)}")
    
    # 3. Save and check DB
    print("\nSaving to database...")
    manager._train_and_save("XGBoost", xgb_model, df, brent, 30)
    
    saved_pred = db.query(Prediction).filter(
        Prediction.commodity_id == brent.id,
        Prediction.model_name == "XGBoost"
    ).first()
    
    if saved_pred:
        print(f"\nSUCCESS: Prediction saved to DB.")
        print(f"Model: {saved_pred.model_name}")
        print(f"Explanation in DB: {saved_pred.explanation}")
    else:
        print("\nFAILURE: Prediction NOT saved to DB.")

    db.close()

if __name__ == "__main__":
    verify()
