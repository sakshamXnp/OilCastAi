import yfinance as yf
import json
from datetime import datetime

tickers = ["BZ=F", "CL=F", "NG=F", "BZ=F", "BRN=F"]

def check_yf():
    res = {}
    for t in tickers:
        try:
            print(f"Checking {t}...")
            ticker = yf.Ticker(t)
            # Try fast_info first
            last_price = ticker.fast_info.get('lastPrice')
            # Also get recent history
            hist = ticker.history(period="1d")
            recent_close = hist['Close'].iloc[-1] if not hist.empty else None
            
            res[t] = {
                "fast_info_price": last_price,
                "history_close": float(recent_close) if recent_close is not None else None,
                "timestamp": str(datetime.now())
            }
        except Exception as e:
            res[t] = {"error": str(e)}
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    check_yf()
