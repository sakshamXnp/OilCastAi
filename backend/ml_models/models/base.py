from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict

class BaseModel(ABC):
    @abstractmethod
    def train(self, df: pd.DataFrame) -> Dict[str, float]:
        """Train model and return metrics (rmse, mae, mape)"""
        pass
        
    @abstractmethod
    def predict(self, days: int = 30) -> pd.DataFrame:
        """Return dataframe with columns ['predicted_price', 'confidence_lower', 'confidence_upper'] indexed by target prediction date"""
        pass
