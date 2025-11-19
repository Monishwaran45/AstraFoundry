"""Google Search tool adapter with retry logic"""

import time
import requests
from typing import List, Dict, Optional
from src.utils.logger import get_logger


class GoogleSearchAdapter:
    """Adapter for Google Search API with retry logic"""
    
    MAX_RETRIES = 2
    RETRY_DELAY_SECONDS = 1
    
    def __init__(self, api_key: Optional[str] = None, engine_id: Optional[str] = None):
        self.api_key = api_key
        self.engine_id = engine_id
        self.logger = get_logger("GoogleSearchAdapter")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search using Google Custom Search API
        Returns list of {title, url, snippet}
        """
        if not self.api_key or not self.engine_id:
            self.logger.warning("Google Search API not configured, returning mock results")
            return self._mock_search(query, num_results)
        
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                params = {
                    'key': self.api_key,
                    'cx': self.engine_id,
                    'q': query,
                    'num': min(num_results, 10)  # API max is 10
                }
                
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for item in data.get('items', [])[:num_results]:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    })
                
                self.logger.info(f"Search successful: {len(results)} results for '{query}'")
                return results
            
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Search attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY_SECONDS * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)
                else:
                    self.logger.error(f"Search failed after {self.MAX_RETRIES + 1} attempts")
                    return self._mock_search(query, num_results)
        
        return []
    
    def _mock_search(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """Return mock search results for testing/fallback"""
        mock_results = []
        for i in range(min(num_results, 3)):
            mock_results.append({
                'title': f"Mock result {i+1} for: {query}",
                'url': f"https://example.com/result{i+1}",
                'snippet': f"This is a mock search result snippet for query: {query}. "
                          f"In production, this would contain real search data."
            })
        return mock_results
