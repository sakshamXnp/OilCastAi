import pandas as pd
import numpy as np
from typing import Dict, List
import logging
from datetime import timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
import xgboost as xgb

from .base import BaseModel

logger = logging.getLogger(__name__)

class XGBoostModel(BaseModel):
    def __init__(self):
        self.model = None
        self.features = []
        self.last_data = None
        self.rmse = 0.0
        self.feature_importance = {}

    def train(self, df: pd.DataFrame) -> Dict[str, float]:
        # Exclude 'target_price' and 'price' from features
        self.features = [c for c in df.columns if c not in ['price', 'target_price']]
        self.last_data = df.iloc[-1:]
        
        X = df[self.features]
        y = df['price']
        
        # Split train/test
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            objective='reg:squarederror',
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        preds = self.model.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        mae = float(mean_absolute_error(y_test, preds))
        mape = float(mean_absolute_percentage_error(y_test, preds))
        
        self.rmse = rmse
        
        # Retrain on all data
        self.model.fit(X, y)
        
        # Capture feature importance
        importances = self.model.feature_importances_
        self.feature_importance = {feat: float(imp) for feat, imp in zip(self.features, importances)}
        
        return {"rmse": rmse, "mae": mae, "mape": mape}

    def predict(self, days: int = 30) -> pd.DataFrame:
        if self.model is None or self.last_data is None:
            return pd.DataFrame()
            
        last_date = self.last_data.index[0]
        future_dates = [last_date + timedelta(days=i) for i in range(1, days + 1)]
        
        predictions = []
        # For multi-step forecasting with external indicators, we'd ideally have forecasts for indicators too.
        # As a simplification, we'll carry forward the last known values for external features.
        
        curr_features = self.last_data[self.features].copy()
        
        for date in future_dates:
            pred_val = self.model.predict(curr_features)[0]
            
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
            
            # Update curr_features for next "pseudo-step" if we used lags, 
            # here we just update price-related features if any (like ma_20)
            # Simplification: we keep technical/econ features static for the forecast window
            pass
            
        df_pred = pd.DataFrame(predictions)
        df_pred.set_index('date', inplace=True)
        return df_pred

    def get_explanation(self) -> str:
        """Generate a text explanation based on feature importance."""
        if not self.feature_importance:
            return "No explanation available."
            
        sorted_imp = sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)
        top_3 = sorted_imp[:3]
        
        factors = []
        for feat, score in top_3:
            if score > 0.05:
                factors.append(f"{feat.replace('_', ' ').title()}")
        
        if not factors:
            return "Price stability influenced by historical trends."
            
        return f"Prediction primarily influenced by: {', '.join(factors)}."
