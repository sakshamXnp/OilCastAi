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
        """Train high-accuracy models for benchmarks and propagate to shadow oils."""
        from data_pipeline.ingestion import YF_TICKERS
        
        # 1. Identify Benchmarks
        benchmarks = self.db.query(Commodity).filter(Commodity.symbol.in_(YF_TICKERS)).all()
        horizons = [7, 30, 90]
        
        for commodity in benchmarks:
            logger.info(f"--- Starting High-Accuracy Training for Benchmark: {commodity.name} ---")
            df = self.fetch_data(commodity)
            
            if len(df) < 40:
                logger.warning(f"Insufficient data for {commodity.name} ({len(df)} points). Skipping.")
                continue

            # Heavy models only for benchmarks to ensure quality
            from ml_models.models.lstm_model import LSTMModel
            from ml_models.models.xgboost_model import XGBoostModel
            
            models = {
                "LSTM": LSTMModel(),
                "XGBoost": XGBoostModel()
            }

            for horizon in horizons:
                for name, model in models.items():
                    try:
                        self._train_and_save(name, model, df, commodity, horizon)
                    except Exception as e:
                        logger.error(f"Failed to train {name} for benchmark {commodity.name}: {e}")
        
        # 2. Propagate Predictions to Shadow Commodities
        self._propagate_predictions_to_shadows()

    def _propagate_predictions_to_shadows(self):
        """Propagate benchmark predictions to related shadow oils using regional spreads."""
        logger.info("Propagating high-accuracy predictions to 100+ shadow blends...")
        from data_pipeline.ingestion import YF_TICKERS
        
        shadows = self.db.query(Commodity).filter(~Commodity.symbol.in_(YF_TICKERS)).all()
        
        for shadow in shadows:
            if not shadow.tracking_benchmark:
                continue
                
            # Find the parent benchmark predictions
            # Note: shadow.tracking_benchmark is 'Brent' or 'WTI'
            benchmark_symbol = "BZ=F" if shadow.tracking_benchmark == "Brent" else "CL=F"
            benchmark = self.db.query(Commodity).filter(Commodity.symbol == benchmark_symbol).first()
            if not benchmark:
                continue
                
            # Copy predictions from benchmark to shadow
            preds = self.db.query(Prediction).filter(Prediction.commodity_id == benchmark.id).all()
            
            stored = 0
            for bp in preds:
                # Apply the spread to the predicted price
                shadow_pred_price = max(1.0, bp.predicted_price + (shadow.current_spread or 0.0))
                shadow_lower = max(1.0, bp.confidence_lower + (shadow.current_spread or 0.0)) if bp.confidence_lower else None
                shadow_upper = max(1.0, bp.confidence_upper + (shadow.current_spread or 0.0)) if bp.confidence_upper else None
                
                # Upsert
                existing = self.db.query(Prediction).filter(
                    Prediction.commodity_id == shadow.id,
                    Prediction.model_name == bp.model_name,
                    Prediction.target_date == bp.target_date,
                    Prediction.horizon_days == bp.horizon_days
                ).first()
                
                if existing:
                    existing.predicted_price = shadow_pred_price
                    existing.confidence_lower = shadow_lower
                    existing.confidence_upper = shadow_upper
                else:
                    self.db.add(Prediction(
                        commodity_id=shadow.id,
                        model_name=bp.model_name,
                        target_date=bp.target_date,
                        predicted_price=shadow_pred_price,
                        confidence_lower=shadow_lower,
                        confidence_upper=shadow_upper,
                        horizon_days=bp.horizon_days,
                        explanation=f"Derived from high-accuracy {shadow.tracking_benchmark} LSTM model with regional spread."
                    ))
                stored += 1
            
            if stored > 0:
                self.db.commit()
                logger.debug(f"Propagated {stored} predictions to {shadow.name}")
            
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
