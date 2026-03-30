import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy.orm import Session
from database.models import NewsEvent

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def fetch_and_analyze_news(self, db: Session, query: str = "crude oil"):
        """Fetch news from Google News RSS and analyze sentiment."""
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            logger.info(f"Fetching news for query: {query}")
            response = requests.get(url)
            if response.status_code != 200:
                logger.error("Failed to fetch news RSS")
                return
                
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            
            for item in items[:50]: # Process top 50 headlines
                title = item.find('title').text
                link = item.find('link').text
                pub_date_str = item.find('pubDate').text
                
                # Extract source name from <source> tag
                source_element = item.find('source')
                source_name = source_element.text if source_element is not None else "Google News"
                
                # Example: 'Fri, 07 Mar 2026 05:12:00 GMT'
                try:
                    pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %Z')
                except ValueError:
                    # Fallback if timezone format differs
                    pub_date = datetime.now()
                
                # Analyze sentiment
                scores = self.analyzer.polarity_scores(title)
                score = scores['compound']
                
                # Check if news already exists
                exists = db.query(NewsEvent).filter(NewsEvent.headline == title).first()
                if not exists:
                    news = NewsEvent(
                        headline=title,
                        source=source_name,
                        url=link,
                        sentiment_score=score,
                        timestamp=pub_date
                    )
                    db.add(news)
            
            db.commit()
            logger.info(f"News sentiment analysis complete. Added/Verified {len(items[:50])} headlines.")
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            db.rollback()

    def get_market_sentiment_score(self, db: Session, hours: int = 24) -> float:
        """Calculate aggregate sentiment score for the last N hours."""
        from sqlalchemy import func
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=hours)
        avg_score = db.query(func.avg(NewsEvent.sentiment_score)).filter(NewsEvent.timestamp >= cutoff).scalar()
        
        return float(avg_score) if avg_score is not None else 0.0
