import time
from typing import Any, Optional, Dict
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

class StockPriceCache:
    """Simple in-memory cache for stock prices with TTL (Time To Live)"""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if cached entry has expired"""
        return time.time() - timestamp > self.ttl_seconds
    
    def get(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get cached stock info if available and not expired"""
        if ticker in self.cache:
            entry = self.cache[ticker]
            if not self._is_expired(entry['timestamp']):
                logger.debug(f"Cache hit for {ticker}")
                return entry['data']
            else:
                logger.debug(f"Cache expired for {ticker}")
                del self.cache[ticker]
        return None
    
    def set(self, ticker: str, data: Dict[str, Any]) -> None:
        """Store stock info in cache"""
        self.cache[ticker] = {
            'data': data,
            'timestamp': time.time()
        }
        logger.debug(f"Cached data for {ticker}")
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> None:
        """Remove expired entries from cache"""
        expired_tickers = [
            ticker for ticker, entry in self.cache.items()
            if self._is_expired(entry['timestamp'])
        ]
        for ticker in expired_tickers:
            del self.cache[ticker]
        if expired_tickers:
            logger.debug(f"Cleaned up expired entries: {expired_tickers}")

# Global cache instance
stock_cache = StockPriceCache()

def get_stock_info_cached(ticker: str) -> Dict[str, Any]:
    """Get stock info with caching"""
    # Check cache first
    cached_data = stock_cache.get(ticker)
    if cached_data:
        return cached_data
    
    # Fetch from yfinance if not in cache
    try:
        logger.info(f"Fetching fresh data for {ticker}")
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Cache the result
        stock_cache.set(ticker, info)
        
        return info
    except Exception as e:
        logger.error(f"Error fetching stock data for {ticker}: {str(e)}")
        # Return minimal data on error
        return {
            'currentPrice': 0,
            'previousClose': 0,
            'longName': ticker,
            'marketCap': 0,
            'dividendRate': 0,
            'dividendYield': 0
        }

def get_multiple_stocks_cached(tickers: list) -> Dict[str, Dict[str, Any]]:
    """Get info for multiple stocks efficiently with caching"""
    results = {}
    uncached_tickers = []
    
    # First, get all cached data
    for ticker in tickers:
        cached_data = stock_cache.get(ticker)
        if cached_data:
            results[ticker] = cached_data
        else:
            uncached_tickers.append(ticker)
    
    # Fetch uncached tickers
    if uncached_tickers:
        try:
            logger.info(f"Fetching fresh data for {len(uncached_tickers)} tickers")
            # yfinance can fetch multiple tickers at once
            tickers_str = ' '.join(uncached_tickers)
            stocks = yf.Tickers(tickers_str)
            
            for ticker in uncached_tickers:
                try:
                    info = stocks.tickers[ticker].info
                    stock_cache.set(ticker, info)
                    results[ticker] = info
                except Exception as e:
                    logger.error(f"Error fetching {ticker}: {str(e)}")
                    results[ticker] = {
                        'currentPrice': 0,
                        'previousClose': 0,
                        'longName': ticker,
                        'marketCap': 0,
                        'dividendRate': 0,
                        'dividendYield': 0
                    }
        except Exception as e:
            logger.error(f"Error in batch fetch: {str(e)}")
            # Fall back to individual fetches
            for ticker in uncached_tickers:
                results[ticker] = get_stock_info_cached(ticker)
    
    return results

# Background cleanup task (optional - can be called periodically)
def cleanup_cache():
    """Clean up expired cache entries"""
    stock_cache.cleanup_expired()