import pandas as pd
import numpy as np
from typing import Dict
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from datetime import timedelta
import logging

from .base import BaseModel

logger = logging.getLogger(__name__)

class LinearRegressionModel(BaseModel):
    def __init__(self):
        self.model = LinearRegression()
        self.last_price = 0.0
        self.last_date = None
        self.rmse = 0.0
        self.features = ['day_of_year', 'year', 'month', 'price_lag_1', 'price_lag_7', 'sentiment']
        
    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df_feats = df.copy()
        # Features are all columns except price and target_price
        self.features = [c for c in df_feats.columns if c not in ['price', 'target_price']]
        return df_feats.dropna()

    def train(self, df: pd.DataFrame) -> Dict[str, float]:
        self.last_price = df['price'].iloc[-1]
        self.last_date = df.index[-1]
        
        df_feats = self._prepare_features(df)
        if df_feats.empty:
            raise ValueError("Not enough data to train linear regression.")
            
        X = df_feats[self.features]
        y = df_feats['price']
        
        # Split train/test (80/20) for metrics
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model.fit(X_train.values, y_train.values)
            preds = self.model.predict(X_test.values)
        
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        mae = float(mean_absolute_error(y_test, preds))
        mape = float(mean_absolute_percentage_error(y_test, preds))
        
        # Retrain on all data
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model.fit(X.values, y.values)
        
        self.rmse = rmse
        return {"rmse": rmse, "mae": mae, "mape": mape}
        
    def predict(self, days: int = 30) -> pd.DataFrame:
        if self.last_date is None or self.model is None:
            return pd.DataFrame()
            
        future_dates = [self.last_date + timedelta(days=i) for i in range(1, days + 1)]
        
        # We'll use the last known feature row as a template
        # In a real system, we'd need forecasts for all features (USD, VIX, etc.)
        # For this MVP, we carry forward the last known state.
        last_row = self.last_df_feats.iloc[-1:][self.features].copy()
        
        predictions = []
        for date in future_dates:
            pred_val = self.model.predict(last_row.values)[0]
            
            # Confidence Interval
            z_score = 1.96
            step = len(predictions) + 1
            error_margin = (self.rmse if self.rmse > 0 else 1.0) * z_score * np.sqrt(step)
            
            predictions.append({
                'date': date,
                'predicted_price': float(pred_val),
                'confidence_lower': float(pred_val - error_margin),
                'confidence_upper': float(pred_val + error_margin)
            })
            
        df_pred = pd.DataFrame(predictions)
        df_pred.set_index('date', inplace=True)
        return df_pred

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        # Exclude 'target_price' and 'price' from features
        self.features = [c for c in df.columns if c not in ['price', 'target_price']]
        self.last_df_feats = df
        return df.dropna()
