import yfinance as yf
import pandas as pd

symbols = [
    'MRBNc1', 'MRBN.L', 'ADN=F', # Murban
    'DBLc1', 'DBLc1=F', 'DUB=F', # Dubai
    'WCS-FC', 'WCS=F', # WCS
    'ORB=COM', 'OPEC', # OPEC
    'TAPIS.SI', 'TAPIS=COM', # Tapis
    'MAYA.MX', 'MAYA', # Maya
    'USCRWCAS:IND'
]

def test():
    for s in symbols:
        try:
            print(f"Testing {s}...")
            data = yf.download(s, period='1d', progress=False)
            if not data.empty:
                print(f"  SUCCESS: {s} has data. Last Price: {data['Close'].iloc[-1].iloc[0] if isinstance(data['Close'], pd.DataFrame) else data['Close'].iloc[-1]}")
            else:
                ticker = yf.Ticker(s)
                fast = ticker.fast_info
                if 'lastPrice' in fast and fast['lastPrice'] is not None:
                    print(f"  SUCCESS (Fast Info): {s} has price {fast['lastPrice']}")
                else:
                    print(f"  FAILED: {s} is empty.")
        except Exception as e:
            print(f"  ERROR: {s} failed with {e}")

if __name__ == "__main__":
    test()
