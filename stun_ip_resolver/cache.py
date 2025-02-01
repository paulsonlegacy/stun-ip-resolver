import os, json, sqlite3, redis, time
from cachetools import TTLCache
#from abc import ABC, abstractmethod



# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(BASE_DIR, "cache.json")
SQLITE_DB = os.path.join(BASE_DIR, "cache.sqlite")


'''
# ================================
# Base Cache Interface
# ================================
class BaseCache(ABC):
    """Abstract base class for different cache backends."""

    @abstractmethod
    def get_cached_info(self, ip):
        pass

    @abstractmethod
    def cache_stun_info(self, ip, port, nat_type, timestamp):
        pass

    @abstractmethod
    def clear_cache(self):
        pass
'''

# ================================
# 1️⃣ In-Memory Cache (TTLCache)
# ================================
class InMemoryCache:
    def __init__(self, max_size=100, ttl=300):
        """Initialize TTL cache with a max size and expiration time (TTL)."""
        self.cache = TTLCache(maxsize=max_size, ttl=ttl)

    def get_cached_info(self, ip):
        """Retrieve STUN info if available in cache."""
        return self.cache.get(ip)

    def cache_stun_info(self, ip, port, nat_type, timestamp):
        """Store STUN info in cache."""
        self.cache[ip] = {
            "data": {"ip": ip, "port": port, "nat_type": nat_type},
            "timestamp": timestamp,
        }

    def clear_cache(self):
        """Clear the entire cache."""
        self.cache.clear()


# ================================
# 2️⃣ File-Based Cache (Persistent)
# ================================
class FileCache:
    def __init__(self, file_path=CACHE_FILE, ttl=300):
        self.file_path = file_path  # Store the file path
        self.ttl = ttl
        self.cache = self._load_cache()  # ✅ Load cache properly

    def cache_stun_info(self, ip, port, nat_type, timestamp):
        """Store STUN info in a file with timestamps."""
        self.cache[ip] = {
            "data": {"ip": ip, "port": port, "nat_type": nat_type},
            "timestamp": timestamp,
        }
        self._save_cache()

    def get_cached_info(self, ip):
        """Retrieve cached STUN info if valid."""
        entry = self.cache.get(ip, None)  # ✅ Now `self.cache` is a dictionary
        if not entry or "timestamp" not in entry:
            return None
        if time.time() - entry["timestamp"] < self.ttl:
            return entry
        return None

    def _load_cache(self):
        """Load cache from file, return empty dict if file does not exist."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}  # Return empty cache if JSON is corrupted
        return {}

    def _save_cache(self):
        """Save updated cache data to file."""
        with open(self.file_path, "w") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=4)



# ================================
# 3️⃣ DB Cache (SQLite3)
# ================================
class SQLiteCache:
    def __init__(self, db_path=SQLITE_DB, ttl=300):
        self.db_path = db_path
        self.ttl = ttl
        self._initialize_db()

    def _initialize_db(self):
        """Ensure table exists with a timestamp column."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                    CREATE TABLE IF NOT EXISTS stun_cache (
                        ip TEXT PRIMARY KEY,
                        port INTEGER,
                        nat_type TEXT,
                        timestamp REAL
                    )
                """
            )

    def cache_stun_info(self, ip, port, nat_type, timestamp):
        """Insert STUN info with timestamp."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "REPLACE INTO stun_cache (ip, port, nat_type, timestamp) VALUES (?, ?, ?, ?)",
                (ip, port, nat_type, timestamp),
            )

    def get_cached_info(self, ip):
        """Retrieve STUN info if not expired, otherwise delete it."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT ip, port, nat_type, timestamp FROM stun_cache WHERE ip=?", (ip,))
            row = cursor.fetchone()
            if row:
                current_time = time.time()
                if current_time - row[3] < self.ttl:
                    return {
                        "data": {"ip": row[0], "port": row[1], "nat_type": row[2]},
                        "timestamp": row[3],
                    }
                conn.execute("DELETE FROM stun_cache WHERE ip=?", (ip,))   # Cleanup expired entry
        return None



# ================================
# 4️⃣ Redis Cache (Distributed + TTL)
# ================================
class RedisCache:
    def __init__(self, redis_url="redis://localhost:6379", ttl=300):
        self.redis = redis.from_url(redis_url)
        self.ttl = ttl

    def cache_stun_info(self, ip, port, nat_type, timestamp):
        """Cache STUN info with automatic expiry."""
        data = json.dumps({
            "data": {"ip": ip, "port": port, "nat_type": nat_type},
            "timestamp": timestamp,
        })
        self.redis.setex(ip, self.ttl, data)  # Automatically expires after `ttl` seconds

    def get_cached_info(self, ip):
        """Retrieve STUN info if available (Redis auto-deletes expired keys)."""
        data = self.redis.get(ip)
        try:
            return json.loads(data) if data else None
        except json.JSONDecodeError:
            return None


# ================================
# Cache Manager (Chooses Backend)
# ================================
class IPResolverCache:
    def __init__(self, backend="memory", ttl=300, **kwargs):  
        """Initialize the appropriate cache backend with TTL support."""
        if backend == "memory":
            self.cache = InMemoryCache(ttl=ttl, **kwargs)  # Pass TTL
        elif backend == "file":
            self.cache = FileCache(ttl=ttl, **kwargs)  # Pass TTL
        elif backend == "sqlite":
            self.cache = SQLiteCache(ttl=ttl, **kwargs)  # Pass TTL
        elif backend == "redis":
            self.cache = RedisCache(ttl=ttl, **kwargs)  # Pass TTL
        else:
            raise ValueError("Invalid cache backend. Use 'memory', 'file', 'sqlite', or 'redis'.")

    def get_cached_info(self, ip):
        """Retrieve cached STUN info if available."""
        return self.cache.get_cached_info(ip)

    def cache_stun_info(self, ip, port, nat_type, timestamp):
        """Store STUN info in cache."""
        self.cache.cache_stun_info(ip, port, nat_type, timestamp)

    def clear_cache(self):
        """Clear all cached data."""
        self.cache.clear_cache()
