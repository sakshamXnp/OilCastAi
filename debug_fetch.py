import pandas as pd
import numpy as np
from datetime import datetime, date

# Simulate the logic in ModelManager.fetch_data
def fetch_data_test():
    idx = pd.to_datetime(['2024-01-01', '2024-01-02'])
    df = pd.DataFrame({"price": [10.0, 11.0]}, index=idx)
    df.index.name = 'date'
    
    # Logic:
    df['sentiment'] = 0.0
    
    # Simulate news
    news_dates = [date(2024, 1, 1)]
    avg_sentiment = pd.Series([0.5], index=news_dates)
    
    # The mapping line:
    df['sentiment'] = [avg_sentiment.get(d, 0.0) for d in df.index.date]
    print("DF with sentiment:")
    print(df)
    
    # Simulate Model training access
    feature_cols = ['price', 'sentiment']
    print("Features access:")
    print(df[feature_cols].values)

if __name__ == "__main__":
    fetch_data_test()
