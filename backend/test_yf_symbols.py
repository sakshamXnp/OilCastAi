import platform
from collections import namedtuple
_uname_res = namedtuple('uname_result', ['system', 'node', 'release', 'version', 'machine', 'processor'])
platform.uname = lambda: _uname_res('Windows', 'Node', '10', '10.0', 'AMD64', 'AMD64')

import yfinance as yf
import pandas as pd

symbols = ["BZ=F", "CL=F", "DUB=F", "NG=F", "RB=F", "HO=F", "LGO=F", "JET=F"]

def test_symbols():
    for symbol in symbols:
        try:
            print(f"Testing {symbol}...")
            data = yf.download(symbol, period="5d", interval="1d", progress=False)
            if data.empty:
                print(f"  FAILED: {symbol} returned empty data")
            else:
                print(f"  SUCCESS: {symbol} returned {len(data)} rows. Last Price: {data['Close'].iloc[-1].iloc[0] if isinstance(data['Close'], pd.DataFrame) else data['Close'].iloc[-1]}")
        except Exception as e:
            print(f"  ERROR: {symbol} threw error: {e}")

if __name__ == "__main__":
    test_symbols()
