import logging
from typing import List
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from database.models import Commodity, PriceData, Prediction, ModelMetric, NewsEvent

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, db: Session):
        self.db = db
        
    def fetch_data(self, commodity: Commodity) -> pd.DataFrame:
        """Fetch historical price data, merge with sentiment and economic indicators, and add technical features."""
        from database.models import EconomicIndicator
        
        # 1. Fetch Prices
        records = self.db.query(PriceData).filter(PriceData.commodity_id == commodity.id).order_by(PriceData.timestamp).all()
        df = pd.DataFrame([{
            "date": r.timestamp,
            "target_price": r.price # Rename to avoid confusion after scaling
        } for r in records])
        
        if df.empty:
            return df
            
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df[~df.index.duplicated(keep='last')]
        df.sort_index(inplace=True)
        # Use business day frequency and interpolate
        df = df.asfreq('B').ffill()
        
        # 2. Technical Features
        # Moving Averages
        df['ma_20'] = df['target_price'].rolling(window=20).mean()
        df['ma_50'] = df['target_price'].rolling(window=50).mean()
        # Volatility (Standard Deviation)
        df['volatility_20'] = df['target_price'].rolling(window=20).std()
        # Price Momentum (RSI proxy)
        change = df['target_price'].diff()
        gain = (change.where(change > 0, 0)).rolling(window=14).mean()
        loss = (-change.where(change < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 3. Sentiment Integration
        df['sentiment'] = 0.0
        sentiment_records = self.db.query(NewsEvent).filter(NewsEvent.timestamp >= df.index.min()).all()
        if sentiment_records:
            sdf = pd.DataFrame([{"date": pd.to_datetime(s.timestamp).date(), "score": s.sentiment_score} for s in sentiment_records])
            avg_sentiment = sdf.groupby('date')['score'].mean()
            df['sentiment'] = [avg_sentiment.get(d, 0.0) for d in df.index.date]
        
        # 4. Economic Indicators Integration
        # We fetch all indicators and merge them
        indicators = ["USD Index", "S&P 500 VIX", "Oil Volatility Index", "Gold"]
        for ind_name in indicators:
            ind_records = self.db.query(EconomicIndicator).filter(
                EconomicIndicator.indicator_name == ind_name,
                EconomicIndicator.timestamp >= df.index.min()
            ).all()
            if ind_records:
                idf = pd.DataFrame([{"date": pd.to_datetime(i.timestamp).date(), "value": i.value} for i in ind_records])
                idf.set_index('date', inplace=True)
                # Map value to df
                df[ind_name.lower().replace(" ", "_").replace("&", "")] = [idf.get('value', {}).get(d, np.nan) for d in df.index.date]
        
        # Final cleanup: forward fill missing economic data and drop initial NaNs from rolling/indicators
        df = df.ffill().dropna()
        # Ensure we have a clean 'price' column for target consistency
        df['price'] = df['target_price']
        
        return df

    def train_all(self):
        """Train models for all commodities and all horizons."""
        commodities = self.db.query(Commodity).all()
        horizons = [7, 30, 90]
        
        for commodity in commodities:
            logger.info(f"Starting training cycle for {commodity.name}...")
            df = self.fetch_data(commodity)
            
            if len(df) < 50: # Lowered threshold for new commodities
                logger.warning(f"Not enough data to train models for {commodity.name}.")
                continue

            # Lazy imports so TensorFlow doesn't block server startup
            from ml_models.models.linear_regression import LinearRegressionModel
            from ml_models.models.arima_model import ARIMAModel
            from ml_models.models.lstm_model import LSTMModel
            from ml_models.models.xgboost_model import XGBoostModel
            
            models = {
                "LinearRegression": LinearRegressionModel(),
                "ARIMA": ARIMAModel(),
                "LSTM": LSTMModel(),
                "XGBoost": XGBoostModel()
            }

            for horizon in horizons:
                best_rmse = float('inf')
                best_model_name = None
                
                for name, model in models.items():
                    try:
                        metrics = self._train_and_save(name, model, df, commodity, horizon)
                        if metrics and metrics.get('rmse', float('inf')) < best_rmse:
                            best_rmse = metrics['rmse']
                            best_model_name = name
                    except Exception as e:
                        logger.error(f"Failed to train {name} for {commodity.name}: {e}")
                
                logger.info(f"Best model for {commodity.name} ({horizon}d): {best_model_name} with RMSE {best_rmse}")
            
    def _train_and_save(self, name, model, df, commodity, horizon):
        logger.info(f"Training {name} for {commodity.name} ({horizon}d horizon)...")
        try:
            metrics = model.train(df)
            explanation = model.get_explanation() if hasattr(model, 'get_explanation') else None
            
            import json
            metrics_json = json.dumps({
                "feature_importance": getattr(model, 'feature_importance', {}),
                "metrics": metrics
            })
            
            # Upsert ML metrics - SQLite compatible
            existing_metric = self.db.query(ModelMetric).filter(
                ModelMetric.commodity_id == commodity.id,
                ModelMetric.model_name == name
            ).first()
            
            if existing_metric:
                existing_metric.rmse = float(metrics.get('rmse', 0))
                existing_metric.mae = float(metrics.get('mae', 0))
                existing_metric.mape = float(metrics.get('mape', 0))
                existing_metric.last_trained = func.now()
            else:
                self.db.add(ModelMetric(
                    commodity_id=commodity.id,
                    model_name=name,
                    rmse=float(metrics.get('rmse', 0)),
                    mae=float(metrics.get('mae', 0)),
                    mape=float(metrics.get('mape', 0))
                ))
            
            # Predict
            predictions = model.predict(days=horizon)
            if not predictions.empty:
                for idx, row in predictions.iterrows():
                    target_dt = pd.to_datetime(idx)
                    if target_dt.tzinfo is None:
                        import pytz
                        target_dt = pytz.UTC.localize(target_dt)
                        
                    # Upsert Prediction - SQLite compatible
                    existing_pred = self.db.query(Prediction).filter(
                        Prediction.commodity_id == commodity.id,
                        Prediction.model_name == name,
                        Prediction.target_date == target_dt,
                        Prediction.horizon_days == horizon
                    ).first()
                    
                    if existing_pred:
                        existing_pred.predicted_price = float(row['predicted_price'])
                        existing_pred.confidence_lower = float(row.get('confidence_lower', 0))
                        existing_pred.confidence_upper = float(row.get('confidence_upper', 0))
                        existing_pred.explanation = explanation
                        existing_pred.metrics_json = metrics_json
                    else:
                        self.db.add(Prediction(
                            commodity_id=commodity.id,
                            model_name=name,
                            target_date=target_dt,
                            predicted_price=float(row['predicted_price']),
                            confidence_lower=float(row.get('confidence_lower', 0)),
                            confidence_upper=float(row.get('confidence_upper', 0)),
                            horizon_days=horizon,
                            explanation=explanation,
                            metrics_json=metrics_json
                        ))
            
            self.db.commit()
            logger.info(f"Finished training {name} for {commodity.name} ({horizon}d).")
            return metrics
        except Exception as e:
            logger.error(f"Error training {name} for {commodity.name}: {str(e)}")
            self.db.rollback()
            return None
