import pandas as pd
import numpy as np
from typing import Dict
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from datetime import timedelta
import logging

# Ensure TF logging is minimized
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

from .base import BaseModel

logger = logging.getLogger(__name__)

class LSTMModel(BaseModel):
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.lookback = 60
        self.last_sequence = None
        self.last_date = None
        self.rmse = 0.0
        self.n_features = 1
        
    def create_dataset(self, dataset):
        X, Y = [], []
        for i in range(len(dataset)-self.lookback-1):
            a = dataset[i:(i+self.lookback), :]
            X.append(a)
            # We predict the first column (price)
            Y.append(dataset[i + self.lookback, 0])
        return np.array(X), np.array(Y)

    def train(self, df: pd.DataFrame) -> Dict[str, float]:
        self.last_date = df.index[-1]
        
        # Features are all columns except predicted target price
        feature_cols = [c for c in df.columns if c not in ['price', 'target_price']]
        self.n_features = len(feature_cols)
        data = df[feature_cols].values
        scaled_data = self.scaler.fit_transform(data)
        
        self.last_sequence = scaled_data[-self.lookback:]
        
        X, y = self.create_dataset(scaled_data)
        
        # Split train/test
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        tf.random.set_seed(42)
        
        self.model = Sequential()
        self.model.add(LSTM(50, return_sequences=True, input_shape=(self.lookback, self.n_features)))
        self.model.add(Dropout(0.2))
        self.model.add(LSTM(50, return_sequences=False))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(25))
        self.model.add(Dense(1))
        
        self.model.compile(optimizer='adam', loss='mean_squared_error')
        self.model.fit(X_train, y_train, batch_size=32, epochs=10, verbose=0)
        
        # Predict on test
        preds_scaled = self.model.predict(X_test, verbose=0)
        
        # Inverse transform requires same number of features
        dummy_preds = np.zeros((len(preds_scaled), self.n_features))
        dummy_preds[:, 0] = preds_scaled.flatten()
        preds = self.scaler.inverse_transform(dummy_preds)[:, 0]
        
        dummy_y = np.zeros((len(y_test), self.n_features))
        dummy_y[:, 0] = y_test
        y_test_unscaled = self.scaler.inverse_transform(dummy_y)[:, 0]
        
        rmse = float(np.sqrt(mean_squared_error(y_test_unscaled, preds)))
        mae = float(mean_absolute_error(y_test_unscaled, preds))
        mape = float(mean_absolute_percentage_error(y_test_unscaled, preds))
        
        self.rmse = rmse
        return {"rmse": rmse, "mae": mae, "mape": mape}
        
    def predict(self, days: int = 30) -> pd.DataFrame:
        if self.model is None or self.last_sequence is None:
            return pd.DataFrame()
            
        future_dates = [self.last_date + timedelta(days=i) for i in range(1, days + 1)]
        predictions = []
        
        curr_seq = self.last_sequence
        
        for _ in range(days):
            curr_seq_reshaped = np.reshape(curr_seq, (1, self.lookback, self.n_features))
            pred_scaled = self.model.predict(curr_seq_reshaped, verbose=0)
            
            # Predict next price
            dummy = np.zeros((1, self.n_features))
            dummy[0, 0] = pred_scaled[0][0]
            pred = self.scaler.inverse_transform(dummy)[0][0]
            predictions.append(pred)
            
            # Update sequence for next iteration
            new_entry = np.zeros((1, self.n_features))
            new_entry[0, 0] = pred_scaled[0][0] # The predicted price (scaled)
            
            if self.n_features > 1:
                # Carry forward all other features from the last known timestep in the current sequence
                new_entry[0, 1:] = curr_seq[-1, 1:]
                
            curr_seq = np.append(curr_seq[1:], new_entry, axis=0)
            
        df_pred = pd.DataFrame(index=future_dates)
        df_pred['predicted_price'] = predictions
        
        # 95% Confidence Interval
        steps = np.arange(1, days + 1)
        z_score = 1.96
        error_margin = (self.rmse if self.rmse > 0 else 1.0) * z_score * np.sqrt(steps)
        
        df_pred['confidence_lower'] = predictions - error_margin
        df_pred['confidence_upper'] = predictions + error_margin
        
        return df_pred
