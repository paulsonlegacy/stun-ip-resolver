import unittest
import asyncio
from unittest.mock import AsyncMock, patch
from conexia.middleware.django import STUNMiddleware

class TestSTUNMiddleware(unittest.TestCase):
    def setUp(self):
        """Set up ASGI middleware instance."""
        self.middleware = STUNMiddleware(lambda req: req)

    @patch("conexia.core.STUNClient.get_stun_info", new_callable=AsyncMock)
    def test_asgi_middleware_attaches_stun_info(self, mock_stun):
        """Test ASGI middleware attaches correct STUN info."""
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
            "client": ("127.0.0.1", 12345),
        }

        mock_stun.return_value = {
            "data": {"ip": "192.0.2.1", "port": 54321, "nat_type": "Full Cone"}
        }

        async def run_test():
            await self.middleware(scope)  # ✅ Pass ASGI scope

            self.assertEqual(scope["original_ip"], "192.0.2.1")
            self.assertEqual(scope["original_port"], 54321)
            self.assertEqual(scope["nat_type"], "Full Cone")

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()