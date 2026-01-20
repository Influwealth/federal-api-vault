"""
Resilient HTTP client with retry logic, rate limiting, and caching.
Shared across all federal API modules.
"""
import time
import json
from typing import Optional, Dict, Any
from pathlib import Path
import requests
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import Config


class CacheStore:
    """Simple file-based cache for API responses."""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.enabled = Config.CACHE_ENABLED
        self.ttl = Config.CACHE_TTL_SECONDS
    
    def _key_to_path(self, key: str) -> Path:
        """Convert cache key to safe filename."""
        safe_key = key.replace("/", "_").replace(":", "_")
        return self.cache_dir / f"{safe_key}.json"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached data if fresh."""
        if not self.enabled:
            return None
        
        cache_file = self._key_to_path(key)
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
            
            if time.time() - data.get("timestamp", 0) > self.ttl:
                cache_file.unlink()
                return None
            
            return data.get("value")
        except Exception:
            return None
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Store data in cache with timestamp."""
        if not self.enabled:
            return
        
        cache_file = self._key_to_path(key)
        try:
            with open(cache_file, "w") as f:
                json.dump({
                    "timestamp": time.time(),
                    "value": value
                }, f, indent=2)
        except Exception:
            pass


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, requests_per_minute: int):
        self.rate = requests_per_minute
        self.tokens = requests_per_minute
        self.last_update = time.time()
    
    def acquire(self) -> None:
        """Block until a token is available."""
        while True:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.rate, self.tokens + elapsed * (self.rate / 60))
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return
            
            time.sleep(0.1)


class FederalAPIClient:
    """HTTP client with retry, rate limiting, and caching for federal APIs."""
    
    def __init__(self, api_name: str, api_key: str, base_url: str, rate_limit: int):
        self.api_name = api_name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.rate_limiter = RateLimiter(rate_limit)
        self.cache = CacheStore()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "WealthBridge-FederalAPIVault/0.1.0",
            "Accept": "application/json"
        })
    
    def _build_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate unique cache key."""
        param_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{self.api_name}_{endpoint}_{param_str}"
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
            use_cache: bool = True) -> Dict[str, Any]:
        """Execute GET request with retry logic and caching."""
        params = params or {}
        cache_key = self._build_cache_key(endpoint, params)
        
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        url = f"{self.base_url}{endpoint}"
        headers = self._get_auth_headers()
        
        last_exception = None
        for attempt in range(Config.MAX_RETRIES):
            try:
                self.rate_limiter.acquire()
                
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=Config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                
                data = response.json()
                if use_cache:
                    self.cache.set(cache_key, data)
                
                return data
            
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < Config.MAX_RETRIES - 1:
                    wait = 2 ** attempt
                    time.sleep(wait)
        
        raise last_exception or Exception(f"Request failed after {Config.MAX_RETRIES} attempts")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Override in subclasses for API-specific auth."""
        if self.api_key:
            return {"X-Api-Key": self.api_key}
        return {}


class SAMClient(FederalAPIClient):
    def __init__(self):
        super().__init__(
            api_name="SAM",
            api_key=Config.SAM_API_KEY,
            base_url=Config.SAM_BASE_URL,
            rate_limit=Config.RATE_LIMIT_SAM
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        return {"X-Api-Key": self.api_key}


class DOLClient(FederalAPIClient):
    def __init__(self):
        super().__init__(
            api_name="DOL",
            api_key=Config.DOL_API_KEY,
            base_url=Config.DOL_BASE_URL,
            rate_limit=Config.RATE_LIMIT_DOL
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        return {}
