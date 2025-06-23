"""
News Analysis and Sentiment Analysis Module
"""
import logging
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import feedparser
from bs4 import BeautifulSoup
import yfinance as yf

from config.settings import config

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """Comprehensive news analysis and sentiment scoring"""
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.news_sources = {
            'reuters': 'http://feeds.reuters.com/reuters/businessNews',
            'yahoo_finance': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'marketwatch': 'http://feeds.marketwatch.com/marketwatch/topstories/',
            'cnbc': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114'
        }
    
    def get_news_from_api(self, symbols: List[str], days_back: int = 7) -> List[Dict]:
        """Get news from News API"""
        if not config.news.news_api_key:
            logger.warning("News API key not configured")
            return []
        
        articles = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        for symbol in symbols:
            try:
                url = f"https://newsapi.org/v2/everything"
                params = {
                    'q': f"{symbol} OR {self._get_company_name(symbol)}",
                    'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d'),
                    'sortBy': 'relevancy',
                    'language': 'en',
                    'apiKey': config.news.news_api_key,
                    'pageSize': 20
                }
                
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get('articles', []):
                        articles.append({
                            'symbol': symbol,
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'content': article.get('content', ''),
                            'url': article.get('url', ''),
                            'source': article.get('source', {}).get('name', ''),
                            'published_at': article.get('publishedAt', ''),
                            'relevance_score': self._calculate_relevance(article, symbol)
                        })
                else:
                    logger.error(f"News API error for {symbol}: {response.status_code}")
            except Exception as e:
                logger.error(f"Error fetching news for {symbol}: {e}")
        
        return articles
    
    def get_news_from_feeds(self, symbols: List[str]) -> List[Dict]:
        """Get news from RSS feeds"""
        articles = []
        
        for source_name, feed_url in self.news_sources.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:  # Limit to 10 articles per source
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    
                    # Check if any symbol is mentioned
                    relevant_symbols = []
                    for symbol in symbols:
                        if (symbol.lower() in title.lower() or 
                            symbol.lower() in summary.lower() or
                            self._get_company_name(symbol).lower() in title.lower() or
                            self._get_company_name(symbol).lower() in summary.lower()):
                            relevant_symbols.append(symbol)
                    
                    if relevant_symbols:
                        articles.append({
                            'symbols': relevant_symbols,
                            'title': title,
                            'description': summary,
                            'url': entry.get('link', ''),
                            'source': source_name,
                            'published_at': entry.get('published', ''),
                            'relevance_score': len(relevant_symbols) / len(symbols)
                        })
            except Exception as e:
                logger.error(f"Error fetching RSS feed {source_name}: {e}")
        
        return articles
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using multiple methods"""
        if not text:
            return {'compound': 0, 'positive': 0, 'negative': 0, 'neutral': 0, 'textblob': 0}
        
        # VADER sentiment
        vader_scores = self.vader_analyzer.polarity_scores(text)
        
        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        
        return {
            'compound': vader_scores['compound'],
            'positive': vader_scores['pos'],
            'negative': vader_scores['neg'],
            'neutral': vader_scores['neu'],
            'textblob': textblob_polarity
        }
    
    def get_symbol_sentiment(self, symbol: str, days_back: int = 7) -> Dict:
        """Get aggregated sentiment for a symbol"""
        # Get news from multiple sources
        api_news = self.get_news_from_api([symbol], days_back)
        feed_news = self.get_news_from_feeds([symbol])
        
        all_articles = api_news + [article for article in feed_news if symbol in article.get('symbols', [])]
        
        if not all_articles:
            return {
                'symbol': symbol,
                'sentiment_score': 0,
                'article_count': 0,
                'positive_articles': 0,
                'negative_articles': 0,
                'neutral_articles': 0
            }
        
        sentiments = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for article in all_articles:
            text = f"{article.get('title', '')} {article.get('description', '')}"
            sentiment = self.analyze_sentiment(text)
            
            # Weight by relevance if available
            weight = article.get('relevance_score', 1.0)
            weighted_sentiment = sentiment['compound'] * weight
            sentiments.append(weighted_sentiment)
            
            if sentiment['compound'] > 0.1:
                positive_count += 1
            elif sentiment['compound'] < -0.1:
                negative_count += 1
            else:
                neutral_count += 1
        
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        return {
            'symbol': symbol,
            'sentiment_score': avg_sentiment,
            'article_count': len(all_articles),
            'positive_articles': positive_count,
            'negative_articles': negative_count,
            'neutral_articles': neutral_count,
            'articles': all_articles[:5]  # Top 5 articles
        }
    
    def get_market_sentiment(self, symbols: List[str]) -> Dict:
        """Get overall market sentiment"""
        symbol_sentiments = []
        
        for symbol in symbols:
            sentiment = self.get_symbol_sentiment(symbol)
            symbol_sentiments.append(sentiment)
        
        if not symbol_sentiments:
            return {'overall_sentiment': 0, 'symbols': []}
        
        # Calculate weighted average (by article count)
        total_weighted_sentiment = 0
        total_articles = 0
        
        for sentiment in symbol_sentiments:
            weight = sentiment['article_count']
            total_weighted_sentiment += sentiment['sentiment_score'] * weight
            total_articles += weight
        
        overall_sentiment = total_weighted_sentiment / total_articles if total_articles > 0 else 0
        
        return {
            'overall_sentiment': overall_sentiment,
            'total_articles': total_articles,
            'symbols': symbol_sentiments
        }
    
    def _get_company_name(self, symbol: str) -> str:
        """Get company name for symbol"""
        company_names = {
            'AAPL': 'Apple',
            'MSFT': 'Microsoft',
            'GOOGL': 'Google',
            'AMZN': 'Amazon',
            'TSLA': 'Tesla',
            'NVDA': 'NVIDIA',
            'META': 'Meta',
            'NFLX': 'Netflix'
        }
        return company_names.get(symbol, symbol)
    
    def _calculate_relevance(self, article: Dict, symbol: str) -> float:
        """Calculate relevance score for an article"""
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        company_name = self._get_company_name(symbol).lower()
        
        relevance = 0.0
        
        # Title mentions
        if symbol.lower() in title:
            relevance += 1.0
        if company_name in title:
            relevance += 0.8
        
        # Description mentions
        if symbol.lower() in description:
            relevance += 0.5
        if company_name in description:
            relevance += 0.4
        
        # Financial keywords
        finance_keywords = ['earnings', 'revenue', 'profit', 'stock', 'shares', 'market', 'trading']
        for keyword in finance_keywords:
            if keyword in title or keyword in description:
                relevance += 0.2
                break
        
        return min(relevance, 2.0)  # Cap at 2.0
    
    def get_economic_calendar(self) -> List[Dict]:
        """Get economic calendar events"""
        try:
            # This is a simplified version - in production, you'd use a proper economic calendar API
            events = []
            
            # Placeholder for economic events
            # You would integrate with services like Alpha Vantage, Trading Economics, etc.
            
            return events
        except Exception as e:
            logger.error(f"Error fetching economic calendar: {e}")
            return []