import platform
from collections import namedtuple
_uname_res = namedtuple('uname_result', ['system', 'node', 'release', 'version', 'machine', 'processor'])
platform.uname = lambda: _uname_res('Windows', 'Node', '10', '10.0', 'AMD64', 'AMD64')

from database import database, models
import json

def check_news():
    db = database.SessionLocal()
    try:
        news_count = db.query(models.NewsEvent).count()
        latest_news = db.query(models.NewsEvent).order_by(models.NewsEvent.timestamp.desc()).limit(5).all()
        
        results = {
            "count": news_count,
            "latest": [
                {
                    "headline": n.headline,
                    "sentiment": n.sentiment_score,
                    "timestamp": str(n.timestamp)
                } for n in latest_news
            ]
        }
        print(json.dumps(results, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    check_news()
