import unittest
from unittest.mock import AsyncMock, patch
from django.test import RequestFactory
from django.conf import settings
from conexia.middleware.django import STUNMiddleware

if not settings.configured:
    settings.configure(
        DEFAULT_CHARSET="utf-8",
        INSTALLED_APPS=["django.contrib.contenttypes"],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        }
    )

class TestDjangoMiddleware(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        """Setup middleware with mock response."""
        self.middleware = STUNMiddleware(lambda req: req)
        self.factory = RequestFactory()

    @patch("conexia.core.STUNClient.get_stun_info", new_callable=AsyncMock)
    async def test_middleware_attaches_stun_info(self, mock_stun):
        """Test that STUN middleware attaches correct data to request."""
        mock_stun.return_value = {
            "data": {"ip": "192.0.2.1", "port": 54321, "nat_type": "Full Cone"}
        }

        request = self.factory.get("/")  # ✅ Django Request Object
        response = await self.middleware(request)

        self.assertEqual(request.original_ip, "192.0.2.1")
        self.assertEqual(request.original_port, 54321)
        self.assertEqual(request.nat_type, "Full Cone")

    @patch("conexia.core.STUNClient.get_stun_info", new_callable=AsyncMock, side_effect=Exception("STUN failure"))
    async def test_middleware_handles_stun_failure(self, mock_stun):
        """Test middleware behavior when STUN server is unreachable."""
        request = self.factory.get("/")  # ✅ Django Request Object
        response = await self.middleware(request)

        self.assertIsNone(request.original_ip)
        self.assertIsNone(request.original_port)
        self.assertIsNone(request.nat_type)

if __name__ == "__main__":
    unittest.main()