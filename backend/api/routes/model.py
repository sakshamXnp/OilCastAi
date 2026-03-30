from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import database, models, schemas

router = APIRouter()

def model_training_task(db: Session, commodity_id: Optional[int] = None):
    try:
        from ml_models.training.manager import ModelManager
        manager = ModelManager(db)
        if commodity_id:
            commodity = db.query(models.Commodity).filter(models.Commodity.id == commodity_id).first()
            if commodity:
                # We'll just call train_all but filter or specialized logic if needed
                # For now, ModelManager.train_all is the main entry. 
                # I'll update manager.py to allow specific commodity training if needed, 
                # but train_all is safer for the demo.
                manager.train_all() 
        else:
            manager.train_all()
    except Exception as e:
        print(f"Background training failed: {e}")
    finally:
        db.close()

@router.post("/train")
def train_models(
    commodity_symbol: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(database.get_db)
):
    comm_id = None
    if commodity_symbol:
        commodity = db.query(models.Commodity).filter(
            models.Commodity.symbol == commodity_symbol.upper()
        ).first()
        if not commodity:
            raise HTTPException(status_code=404, detail="Commodity not found")
        comm_id = commodity.id
        
    # Launch background task
    bg_db = database.SessionLocal()
    background_tasks.add_task(model_training_task, bg_db, comm_id)
    
    msg = f"Training started for {commodity_symbol}" if commodity_symbol else "Full platform training started"
    return {"message": msg}

@router.get("/metrics", response_model=List[schemas.ModelMetric])
def get_all_metrics(db: Session = Depends(database.get_db)):
    """Returns all model performance metrics across all commodities."""
    return db.query(models.ModelMetric).all()

@router.get("/metrics/{commodity_symbol}", response_model=List[schemas.ModelMetric])
def get_metrics(commodity_symbol: str, db: Session = Depends(database.get_db)):
    commodity = db.query(models.Commodity).filter(
        models.Commodity.symbol == commodity_symbol.upper()
    ).first()
    
    if not commodity:
        commodity = db.query(models.Commodity).filter(
            models.Commodity.name.ilike(f"%{commodity_symbol}%")
        ).first()

    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")
        
    return db.query(models.ModelMetric).filter(
        models.ModelMetric.commodity_id == commodity.id
    ).all()
