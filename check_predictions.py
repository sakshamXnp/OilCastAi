from database import database
from database.models import Prediction
from sqlalchemy import func
import json

def check():
    print("Initializing DB session...")
    db = database.SessionLocal()
    print("DB session initialized.")
    try:
        print("Querying prediction counts...")
        counts = db.query(Prediction.model_name, func.count(Prediction.id)).group_by(Prediction.model_name).all()
        print(f"Prediction counts: {counts}")
        
        print("Querying sample explanation...")
        sample = db.query(Prediction).filter(Prediction.explanation != None).first()
        if sample:
            print(f"Sample Model: {sample.model_name}")
            print(f"Sample Explanation: {sample.explanation}")
            print(f"Sample Metrics JSON: {sample.metrics_json[:100]}...")
        else:
            print("No predictions with explanations found yet.")
    except Exception as e:
        print(f"Error during check: {e}")
    finally:
        db.close()
        print("DB session closed.")

if __name__ == "__main__":
    check()
