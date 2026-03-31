import yfinance as yf
import pandas as pd

symbols = [
    'BZ=F', 'CL=F', # Brent, WTI (Known working)
    'MAYA.MX', 'MAYA', # Maya
    'DBLc1=F', 'DBLc1', 'DUB=F', # Dubai
    'OQ=F', 'OQ1!', # Oman
    'GSO=F', 'LGO=F', 'ULS=F', # Gasoil
    'PGC=F', 'PN=F', 'PRP=F', # Propane
    'ETF=F', # Ethane
    'RB=F', 'HO=F', 'NG=F', 'JET=F' # Others
]

def test():
    results = {}
    for s in symbols:
        try:
            print(f"Testing {s}...")
            # Try fast_info first for price
            ticker = yf.Ticker(s)
            price = ticker.fast_info.get('lastPrice')
            
            # Try history
            data = yf.download(s, period='5d', progress=False)
            
            status = "FAILED"
            if not data.empty:
                status = "SUCCESS (History)"
                price = data['Close'].iloc[-1]
                if isinstance(price, pd.Series): price = price.iloc[0]
            elif price:
                status = "SUCCESS (Live Only)"
            
            results[s] = {"status": status, "price": str(price)}
            print(f"  {status}: {price}")
        except Exception as e:
            print(f"  ERROR: {s} -> {e}")
            results[s] = {"status": "ERROR", "msg": str(e)}
            
    import json
    with open('symbol_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    test()
