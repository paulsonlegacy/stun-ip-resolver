import os
import json
import sqlite3
import redis
from cachetools import TTLCache
from abc import ABC, abstractmethod

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(BASE_DIR, "stun_cache.json")
SQLITE_DB = os.path.join(BASE_DIR, "stun_cache.sqlite")


# ================================
# Base Cache Interface
# ================================
class BaseCache(ABC):
    """Abstract base class for different cache backends."""

    @abstractmethod
    def get_cached_info(self, ip):
        pass

    @abstractmethod
    def cache_stun_info(self, ip, port, nat_type):
        pass

    @abstractmethod
    def clear_cache(self):
        pass


# ================================
# 1️⃣ In-Memory Cache (TTLCache)
# ================================
class InMemoryCache(BaseCache):
    def __init__(self, max_size=100, ttl=300):
        self.cache = TTLCache(maxsize=max_size, ttl=ttl)

    def get_cached_info(self, ip):
        return self.cache.get(ip, None)

    def cache_stun_info(self, ip, port, nat_type):
        self.cache[ip] = {"ip": ip, "port": port, "nat_type": nat_type}

    def clear_cache(self):
        self.cache.clear()


# ================================
# 2️⃣ File-Based Cache (Persistent)
# ================================
class FileCache(BaseCache):
    def __init__(self, ttl=300):
        self.ttl = ttl
        self.cache = self.load_cache()

    def get_cached_info(self, ip):
        return self.cache.get(ip, None)

    def cache_stun_info(self, ip, port, nat_type):
        self.cache[ip] = {"ip": ip, "port": port, "nat_type": nat_type}
        self.save_cache()

    def clear_cache(self):
        self.cache = {}
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)

    def save_cache(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f)

    def load_cache(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}


# ================================
# 3️⃣ DB Cache (SQLite3)
# ================================
class SQLiteCache(BaseCache):
    def __init__(self, db_path=SQLITE_DB):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS stun_cache (
                    ip TEXT PRIMARY KEY,
                    port INTEGER,
                    nat_type TEXT
                )
                """
            )

    def get_cached_info(self, ip):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT ip, port, nat_type FROM stun_cache WHERE ip = ?", (ip,))
            row = cursor.fetchone()
            return {"ip": row[0], "port": row[1], "nat_type": row[2]} if row else None

    def cache_stun_info(self, ip, port, nat_type):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO stun_cache (ip, port, nat_type) VALUES (?, ?, ?)",
                (ip, port, nat_type),
            )

    def clear_cache(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM stun_cache")


# ================================
# 4️⃣ Redis Cache (Distributed + TTL)
# ================================
class RedisCache(BaseCache):
    def __init__(self, host="localhost", port=6379, db=0, ttl=300):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl = ttl

    def get_cached_info(self, ip):
        data = self.redis.get(ip)
        return json.loads(data) if data else None

    def cache_stun_info(self, ip, port, nat_type):
        self.redis.setex(ip, self.ttl, json.dumps({"ip": ip, "port": port, "nat_type": nat_type}))

    def clear_cache(self):
        self.redis.flushdb()


# ================================
# Cache Manager (Chooses Backend)
# ================================
class IPResolverCache:
    def __init__(self, backend="memory", **kwargs):  # Default to 'memory'
        if backend == "memory":
            self.cache = InMemoryCache(**kwargs)
        elif backend == "file":
            self.cache = FileCache(**kwargs)
        elif backend == "sqlite":
            self.cache = SQLiteCache(**kwargs)
        elif backend == "redis":
            self.cache = RedisCache(**kwargs)
        else:
            raise ValueError("Invalid cache backend. Use 'memory', 'file', 'sqlite' or 'redis'.")

    def get_cached_info(self, ip):
        return self.cache.get_cached_info(ip)

    def cache_stun_info(self, ip, port, nat_type):
        self.cache.cache_stun_info(ip, port, nat_type)

    def clear_cache(self):
        self.cache.clear_cache()