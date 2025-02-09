import unittest
from unittest.mock import patch, AsyncMock
from conexia.core import STUNClient
from conexia.cache import IPResolverCache

class TestSTUNClient(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        """Setup test client with mock cache."""
        self.client = STUNClient(cache_backend="memory", ttl=300)

    @patch("stun.get_ip_info", return_value=("Full-Cone NAT", "203.0.113.1", 45678))
    async def test_get_stun_info(self, mock_stun):
        """Test that STUNClient fetches and caches STUN info correctly."""
        result = await self.client.get_stun_info()
        
        self.assertIn("user_id", result)
        self.assertEqual(result["data"]["ip"], "203.0.113.1")
        self.assertEqual(result["data"]["port"], 45678)
        self.assertEqual(result["data"]["nat_type"], "Full-Cone NAT")

    async def test_caching(self):
        """Test caching functionality (should return the same cached values)."""
        self.client.cache.cache_stun_info("test_user", "198.51.100.2", 55555, "Symmetric NAT", 1700000000)

        cached_result = self.client.cache.get_cached_info("test_user")
        
        self.assertIsNotNone(cached_result)
        self.assertEqual(cached_result["data"]["ip"], "198.51.100.2")

    @patch("stun.get_ip_info", side_effect=Exception("STUN server unreachable"))
    async def test_stun_resolution_error(self, mock_stun):
        """Test handling of STUN resolution failure."""
        with self.assertRaises(Exception) as context:
            await self.client.get_stun_info()
        
        self.assertIn("STUN server unreachable", str(context.exception))

if __name__ == "__main__":
    unittest.main()
