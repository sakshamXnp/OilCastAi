import pandas as pd
import numpy as np
from typing import Dict
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
import logging

from .base import BaseModel

logger = logging.getLogger(__name__)

class ARIMAModel(BaseModel):
    def __init__(self):
        self.model = None
        
    def train(self, df: pd.DataFrame) -> Dict[str, float]:
        df_ts = df['price'].asfreq('B') # Business days
        df_ts = df_ts.ffill()
        
        if len(df_ts) < 50:
            raise ValueError("Not enough data for ARIMA")
            
        # Split train/test
        split_idx = int(len(df_ts) * 0.9)
        train_data, test_data = df_ts.iloc[:split_idx], df_ts.iloc[split_idx:]
        
        try:
            # Train ARIMA(5,1,0) as a baseline
            model_fit = ARIMA(train_data, order=(5,1,0)).fit()
            preds = model_fit.forecast(steps=len(test_data))
            
            rmse = float(np.sqrt(mean_squared_error(test_data, preds)))
            mae = float(mean_absolute_error(test_data, preds))
            mape = float(mean_absolute_percentage_error(test_data, preds))
        except Exception as e:
            logger.error(f"Failed ARIMA Eval: {str(e)}")
            rmse, mae, mape = 0, 0, 0
            
        # Retrain on full data
        self.model = ARIMA(df_ts, order=(5,1,0)).fit()
        
        return {"rmse": rmse, "mae": mae, "mape": mape}
        
    def predict(self, days: int = 30) -> pd.DataFrame:
        if self.model is None:
            return pd.DataFrame()
            
        forecast_obj = self.model.get_forecast(steps=days)
        pred_means = forecast_obj.predicted_mean
        conf_int = forecast_obj.conf_int()
        
        df_pred = pd.DataFrame({
            'predicted_price': pred_means.values,
            'confidence_lower': conf_int.iloc[:, 0].values,
            'confidence_upper': conf_int.iloc[:, 1].values
        }, index=pred_means.index)
        
        return df_pred
