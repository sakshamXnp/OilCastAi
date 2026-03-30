from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Commodity(Base):
    __tablename__ = "commodities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False) # e.g., 'Brent Crude'
    symbol = Column(String, index=True, unique=True, nullable=False) # e.g., 'BZ=F'
    category = Column(String, index=True, nullable=False) # 'CRUDE', 'REFINED'
    region = Column(String, index=True, nullable=True) # 'Global', 'USA', 'Europe'
    
    prices = relationship("PriceData", back_populates="commodity")
    predictions = relationship("Prediction", back_populates="commodity")
    metrics = relationship("ModelMetric", back_populates="commodity")

class PriceData(Base):
    __tablename__ = "price_data"

    id = Column(Integer, primary_key=True, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    source = Column(String, default="yfinance")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    commodity = relationship("Commodity", back_populates="prices")
    __table_args__ = (UniqueConstraint('commodity_id', 'timestamp', name='uix_commodity_timestamp'),)

class EconomicIndicator(Base):
    __tablename__ = "economic_indicators"

    id = Column(Integer, primary_key=True, index=True)
    indicator_name = Column(String, index=True, nullable=False) # e.g., 'USD Index'
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    source = Column(String, default="stooq")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (UniqueConstraint('indicator_name', 'timestamp', name='uix_indicator_timestamp'),)

class NewsEvent(Base) :
    __tablename__ = "news_events"

    id = Column(Integer, primary_key=True, index=True)
    headline = Column(String, nullable=False)
    source = Column(String, nullable=True)
    url = Column(String, nullable=True) # Link to article
    sentiment_score = Column(Float, nullable=False) # -1.0 to 1.0
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False)
    model_name = Column(String, index=True, nullable=False)
    target_date = Column(DateTime(timezone=True), index=True, nullable=False)
    predicted_price = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    horizon_days = Column(Integer, default=30)
    explanation = Column(String, nullable=True) # Text summary of prediction factors
    metrics_json = Column(String, nullable=True) # JSON string for feature importance/drivers
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    commodity = relationship("Commodity", back_populates="predictions")
    __table_args__ = (UniqueConstraint('commodity_id', 'model_name', 'target_date', 'horizon_days', name='uix_pred_comm_model_date'),)

class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False)
    model_name = Column(String, index=True, nullable=False)
    rmse = Column(Float, nullable=False)
    mae = Column(Float, nullable=False)
    mape = Column(Float, nullable=False)
    last_trained = Column(DateTime(timezone=True), server_default=func.now())
    
    commodity = relationship("Commodity", back_populates="metrics")
    __table_args__ = (UniqueConstraint('commodity_id', 'model_name', name='uix_metric_comm_model'),)
