# Import necessary modules
import os  # For file and directory path operations
import time  # For handling time-based operations like TTL expiry
import json  # For handling JSON data storage in file caching
import unittest  # For running unit tests
import sqlite3  # For handling SQLite database caching
import redis  # For handling Redis-based caching

# Import caching classes from the 'conexia.cache' module
from conexia.cache import InMemoryCache, FileCache, SQLiteCache, RedisCache

# Define constants for file-based and SQLite cache paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file
TEST_CACHE_FILE = os.path.join(BASE_DIR, "test_cache.json")  # File path for JSON-based file cache
TEST_DB = os.path.join(BASE_DIR, "test_cache.sqlite")  # File path for SQLite-based cache


# Unit test class for InMemoryCache
class TestInMemoryCache(unittest.TestCase):
    def setUp(self):
        """Set up the in-memory cache with a max size of 10 and a TTL (Time-To-Live) of 2 seconds."""
        self.cache = InMemoryCache(max_size=10, ttl=2)

    def test_cache_stun_info(self):
        """Test storing and retrieving STUN info from the in-memory cache."""
        self.cache.cache_stun_info("user123", "192.168.1.1", 5000, "Full Cone", time.time())
        cached_data = self.cache.get_cached_info("user123")
        self.assertIsNotNone(cached_data)  # Ensure data is stored
        self.assertEqual(cached_data["data"]["ip"], "192.168.1.1")  # Verify stored IP

    def test_cache_expiry(self):
        """Test that cached data expires after the TTL period (2 seconds)."""
        self.cache.cache_stun_info("user123", "192.168.1.1", 5000, "Full Cone", time.time())
        time.sleep(3)  # Wait for TTL to expire
        cached_data = self.cache.get_cached_info("user123")
        self.assertIsNone(cached_data)  # Ensure expired data is removed

    def test_clear_cache(self):
        """Test that clearing the cache removes the stored entry."""
        self.cache.cache_stun_info("user123", "192.168.1.1", 5000, "Full Cone", time.time())
        self.cache.clear_cache("user123")  # Clear cache for this key
        self.assertIsNone(self.cache.get_cached_info("user123"))  # Ensure data is removed


# Unit test class for FileCache
class TestFileCache(unittest.TestCase):
    def setUp(self):
        """Set up the file-based cache with a JSON file and a TTL of 2 seconds."""
        self.cache = FileCache(file_path=TEST_CACHE_FILE, ttl=2)

    def tearDown(self):
        """Clean up the test file after each test."""
        if os.path.exists(TEST_CACHE_FILE):
            os.remove(TEST_CACHE_FILE)

    def test_cache_stun_info(self):
        """Test storing and retrieving STUN info from the file-based cache."""
        self.cache.cache_stun_info("user123", "192.168.1.1", 5000, "Full Cone", time.time())
        cached_data = self.cache.get_cached_info("user123")
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data["data"]["ip"], "192.168.1.1")

    def test_cache_expiry(self):
        """Test that cached data expires after the TTL period (2 seconds)."""
        self.cache.cache_stun_info("user123", "192.168.1.1", 5000, "Full Cone", time.time())
        time.sleep(3)
        self.assertIsNone(self.cache.get_cached_info("user123"))

    def test_clear_cache(self):
        """Test that clearing the cache removes the stored entry."""
        self.cache.cache_stun_info("user123", "192.168.1.1", 5000, "Full Cone", time.time())
        self.cache.clear_cache("user123")
        self.assertIsNone(self.cache.get_cached_info("user123"))


# Unit test class for SQLiteCache
class TestSQLiteCache(unittest.TestCase):
    def setUp(self):
        """Set up the SQLite-based cache with a database file and a TTL of 2 seconds."""
        self.cache = SQLiteCache(db_path=TEST_DB, ttl=2)

    def tearDown(self):
        """Clean up the test database file after each test."""
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_cache_stun_info(self):
        """Test storing and retrieving STUN info from the SQLite-based cache."""
        self.cache.cache_stun_info("user123", "192.168.1.1", 5000, "Full Cone", time.time())
        cached_data = self.cache.get_cached_info("user123")
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data["data"]["ip"], "192.168.1.1")

    def test_cache_expiry(self):
        """Test that cached data expires after the TTL period (2 seconds)."""
        self.cache.cache_stun_info("user123", "192.168.1.1", 5000, "Full Cone", time.time())
        time.sleep(3)
        self.assertIsNone(self.cache.get_cached_info("user123"))

    def test_clear_cache(self):
        """Test that clearing the cache removes the stored entry."""
        self.cache.cache_stun_info("user123", "192.168.1.1", 5000, "Full Cone", time.time())
        self.cache.clear_cache("user123")
        self.assertIsNone(self.cache.get_cached_info("user123"))


# Unit test class for RedisCache
class TestRedisCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the Redis-based cache using a local Redis server before running tests."""
        cls.redis_client = redis.Redis(host="localhost", port=6379, db=0)  # Connect to Redis
        cls.redis_client.flushdb()  # Clear the Redis database to avoid conflicts
        cls.cache = RedisCache(redis_url="redis://localhost:6379", ttl=2)

    @classmethod
    def tearDownClass(cls):
        """Clean up Redis database after all tests."""
        cls.redis_client.flushdb()

    def test_cache_stun_info(self):
        """Test storing and retrieving STUN info from the Redis-based cache."""
        self.cache.cache_stun_info("user123", "192.168.1.1", 5000, "Full Cone", time.time())
        cached_data = self.cache.get_cached_info("user123")
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data["data"]["ip"], "192.168.1.1")

    def test_cache_expiry(self):
        """Test that cached data expires after the TTL period (2 seconds)."""
        self.cache.cache_stun_info("user123", "192.168.1.1", 5000, "Full Cone", time.time())
        time.sleep(3)
        self.assertIsNone(self.cache.get_cached_info("user123"))

    def test_clear_cache(self):
        """Test that clearing the cache removes the stored entry."""
        self.cache.cache_stun_info("user123", "192.168.1.1", 5000, "Full Cone", time.time())
        self.cache.clear_cache("user123")
        self.assertIsNone(self.cache.get_cached_info("user123"))


# Run all unit tests when this script is executed directly
if __name__ == "__main__":
    unittest.main()
