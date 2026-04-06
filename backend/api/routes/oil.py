from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import database, models, schemas

router = APIRouter()

@router.get("/commodities", response_model=List[schemas.Commodity])
def get_commodities(db: Session = Depends(database.get_db)):
    return db.query(models.Commodity).all()

@router.get("/prices/{commodity_symbol}", response_model=List[schemas.PriceData])
def get_historical_prices(
    commodity_symbol: str,
    days: int = 30,
    db: Session = Depends(database.get_db)
):
    commodity = db.query(models.Commodity).filter(
        models.Commodity.symbol == commodity_symbol.upper()
    ).first()
    
    if not commodity:
        # Try matching by name if symbol fails
        commodity = db.query(models.Commodity).filter(
            models.Commodity.name.ilike(f"%{commodity_symbol}%")
        ).first()
        
    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")
        
    cutoff_date = datetime.now() - timedelta(days=days)
    return db.query(models.PriceData).filter(
        models.PriceData.commodity_id == commodity.id,
        models.PriceData.timestamp >= cutoff_date
    ).order_by(models.PriceData.timestamp.asc()).all()

@router.get("/predict/{commodity_symbol}", response_model=List[schemas.Prediction])
def get_predictions(
    commodity_symbol: str,
    horizon: int = 30,
    model: str = "LSTM",
    db: Session = Depends(database.get_db)
):
    commodity = db.query(models.Commodity).filter(
        models.Commodity.symbol == commodity_symbol.upper()
    ).first()
    
    if not commodity:
        commodity = db.query(models.Commodity).filter(
            models.Commodity.name.ilike(f"%{commodity_symbol}%")
        ).first()

    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")
        
    today = datetime.now() - timedelta(days=1)
    return db.query(models.Prediction).filter(
        models.Prediction.commodity_id == commodity.id,
        models.Prediction.model_name == model,
        models.Prediction.horizon_days == horizon,
        models.Prediction.target_date >= today
    ).order_by(models.Prediction.target_date.asc()).all()

@router.get("/sentiment", response_model=List[schemas.NewsEvent])
def get_market_sentiment(
    days: int = 7,
    db: Session = Depends(database.get_db)
):
    cutoff = datetime.now() - timedelta(days=days)
    return db.query(models.NewsEvent).filter(
        models.NewsEvent.timestamp >= cutoff
    ).order_by(models.NewsEvent.timestamp.desc()).all()

@router.get("/sentiment/score")
def get_sentiment_score(db: Session = Depends(database.get_db)):
    from data_pipeline.sentiment_analyzer import SentimentAnalyzer
    analyzer = SentimentAnalyzer()
    score = analyzer.get_market_sentiment_score(db)
    return {"score": score, "status": "bullish" if score > 0.05 else "bearish" if score < -0.05 else "neutral"}

@router.get("/latest-prices")
def get_latest_prices(db: Session = Depends(database.get_db)):
    from sqlalchemy import func
    commodities = db.query(models.Commodity).all()
    results = []

    for comm in commodities:
        # Get last 2 prices
        last_two = db.query(models.PriceData).filter(
            models.PriceData.commodity_id == comm.id
        ).order_by(models.PriceData.timestamp.desc()).limit(2).all()

        price = 0.0
        timestamp = datetime.now()
        change = 0.0

        if last_two:
            latest = last_two[0]
            price = latest.price
            timestamp = latest.timestamp
            if len(last_two) > 1:
                prev = last_two[1]
                if prev.price != 0:
                    change = ((latest.price - prev.price) / prev.price) * 100

        results.append({
            "symbol": comm.symbol,
            "name": comm.name,
            "price": price,
            "timestamp": timestamp,
            "change": round(change, 2),
            "category": comm.category,
            "region": comm.region,
            "status": "Operational" if last_two else "Pending",
            "tracking_benchmark": comm.tracking_benchmark,
            "current_spread": comm.current_spread
        })

    return results


# Category display order and labels matching oilprice.com
CATEGORY_MAP = {
    "futures_indexes": "FUTURES",
    "opec_members": "OPEC",
    "international": "INTERNATIONAL",
    "canadian_blends": "CANADIAN",
    "us_blends": "US_BLEND",
}

# DB category string (any casing) -> response bucket key
_CATEGORY_BUCKET = {v.upper(): k for k, v in CATEGORY_MAP.items()}


def _oil_prices_bucket_key(category: Optional[str]) -> str:
    if not category or not str(category).strip():
        return "other_benchmarks"
    norm = str(category).strip().upper()
    return _CATEGORY_BUCKET.get(norm, "other_benchmarks")


@router.get("/oil-prices")
def get_oil_prices(db: Session = Depends(database.get_db)):
    """
    Returns all oil commodities with latest prices, grouped by category
    matching oilprice.com's structure.
    """
    commodities = db.query(models.Commodity).all()
    
    result = {
        "futures_indexes": [],
        "opec_members": [],
        "international": [],
        "canadian_blends": [],
        "us_blends": [],
        "other_benchmarks": [],
    }

    for comm in commodities:
        # Get last 2 prices for change calculation
        last_two = db.query(models.PriceData).filter(
            models.PriceData.commodity_id == comm.id
        ).order_by(models.PriceData.timestamp.desc()).limit(2).all()

        price = 0.0
        prev_price = 0.0
        timestamp = None
        change = 0.0
        change_pct = 0.0
        has_data = len(last_two) > 0

        if last_two:
            latest = last_two[0]
            price = round(latest.price, 2)
            timestamp = latest.timestamp.isoformat() if latest.timestamp else None
            if len(last_two) > 1:
                prev_price = last_two[1].price
                if prev_price != 0:
                    change = round(price - prev_price, 2)
                    change_pct = round(((price - prev_price) / prev_price) * 100, 2)

        entry = {
            "symbol": comm.symbol,
            "name": comm.name,
            "price": price,
            "change": change,
            "change_pct": change_pct,
            "timestamp": timestamp,
            "region": comm.region,
            "has_data": has_data,
            "tracking_benchmark": comm.tracking_benchmark,
            "current_spread": comm.current_spread
        }

        bucket = _oil_prices_bucket_key(comm.category)
        result[bucket].append(entry)

    return result

@router.get("/health")
def health_check():
    return {"status": "operational"}

@router.get("/debug/db")
def debug_db(db: Session = Depends(database.get_db)):
    import os
    from config import settings
    commodities = db.query(models.Commodity).count()
    prices = db.query(models.PriceData).count()
    comms = [{"id": c.id, "symbol": c.symbol, "name": c.name, "category": c.category} for c in db.query(models.Commodity).all()]
    return {
        "database_url": settings.DATABASE_URL,
        "cwd": os.getcwd(),
        "db_file_exists": os.path.exists("oilcast.db"),
        "db_file_size": os.path.getsize("oilcast.db") if os.path.exists("oilcast.db") else None,
        "commodities_count": commodities,
        "prices_count": prices,
        "commodities": comms
    }
