from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class CommodityBase(BaseModel):
    name: str
    symbol: str
    category: str
    region: Optional[str] = None

class Commodity(CommodityBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class PriceDataBase(BaseModel):
    commodity_id: int
    price: float
    timestamp: datetime
    source: str

class PriceData(PriceDataBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EconomicIndicatorBase(BaseModel):
    indicator_name: str
    value: float
    timestamp: datetime
    source: str

class EconomicIndicator(EconomicIndicatorBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class NewsEventBase(BaseModel):
    headline: str
    source: Optional[str] = None
    url: Optional[str] = None
    sentiment_score: float
    timestamp: datetime

class NewsEvent(NewsEventBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PredictionBase(BaseModel):
    commodity_id: int
    model_name: str
    target_date: datetime
    predicted_price: float
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None
    horizon_days: int
    explanation: Optional[str] = None
    metrics_json: Optional[str] = None

class Prediction(PredictionBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ModelMetricBase(BaseModel):
    commodity_id: int
    model_name: str
    rmse: float
    mae: float
    mape: float

class ModelMetric(ModelMetricBase):
    id: int
    last_trained: datetime
    model_config = ConfigDict(from_attributes=True)
