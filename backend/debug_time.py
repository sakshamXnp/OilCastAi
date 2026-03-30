import platform
from collections import namedtuple
_uname_res = namedtuple('uname_result', ['system', 'node', 'release', 'version', 'machine', 'processor'])
platform.uname = lambda: _uname_res('Windows', 'Node', '10', '10.0', 'AMD64', 'AMD64')

from datetime import datetime
from database import database, models

def debug_time():
    db = database.SessionLocal()
    try:
        now = datetime.now()
        print(f"datetime.now(): {now}")
        
        latest_news = db.query(models.NewsEvent).order_by(models.NewsEvent.timestamp.desc()).first()
        if latest_news:
            print(f"Latest News ID: {latest_news.id}")
            print(f"Latest News Headline: {latest_news.headline[:50]}...")
            print(f"Latest News Timestamp: {latest_news.timestamp}")
            
            diff = latest_news.timestamp - now
            print(f"Difference (News - Now): {diff}")
            
            # Check filtering logic
            days = 7
            cutoff = now - (latest_news.timestamp - latest_news.timestamp) # mockup
            cutoff_7d = now - (latest_news.timestamp - latest_news.timestamp) # mockup
            # Actual cutoff used in API
            import datetime as dt
            api_cutoff = now - dt.timedelta(days=7)
            print(f"API Cutoff (7 days ago): {api_cutoff}")
            
            match_count = db.query(models.NewsEvent).filter(models.NewsEvent.timestamp >= api_cutoff).count()
            print(f"News matching cutoff (>= {api_cutoff}): {match_count}")
            
        else:
            print("No news found in database.")
    finally:
        db.close()

if __name__ == "__main__":
    debug_time()
