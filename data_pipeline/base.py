from abc import ABC, abstractmethod
import pandas as pd
from sqlalchemy.orm import Session
from database.models import Commodity

class BaseSource(ABC):
    @abstractmethod
    def fetch(self, commodity: Commodity, days: int = 365) -> pd.DataFrame:
        """Fetch historical data for a specific commodity.
        Returns a DataFrame with columns ['timestamp', 'price']."""
        pass

    @abstractmethod
    def fetch_live(self, commodity: Commodity) -> float:
        """Fetch current live price."""
        pass
