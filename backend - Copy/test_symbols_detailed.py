import yfinance as yf
import pandas as pd

symbols = ['PGC=F', 'PN=F', 'PRP=F', 'LGO=F', 'GSO=F', 'ULS=F', 'RB=F', 'NG=F']

def test():
    for s in symbols:
        try:
            print(f"Testing {s}...")
            data = yf.download(s, period='5d', progress=False)
            if not data.empty:
                print(f"  SUCCESS: {s} has {len(data)} rows.")
            else:
                print(f"  FAILED: {s} is empty.")
        except Exception as e:
            print(f"  ERROR: {s} failed with {e}")

if __name__ == "__main__":
    test()
