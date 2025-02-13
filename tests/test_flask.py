import unittest
from unittest.mock import patch, AsyncMock
from flask import Flask, request
from conexia.middleware.flask import STUNMiddleware

class TestSTUNMiddleware(unittest.TestCase):
    def setUp(self):
        """Set up Flask test app with STUN middleware."""
        self.app = Flask(__name__)
        self.middleware = STUNMiddleware(self.app)
        self.client = self.app.test_client()

    @patch("conexia.core.STUNClient.get_stun_info", new_callable=AsyncMock)
    def test_middleware_attaches_stun_info(self, mock_stun):
        """Test that STUN middleware attaches correct data to the request."""
        mock_stun.return_value = {
            "data": {"ip": "192.0.2.1", "port": 54321, "nat_type": "Full Cone"}
        }

        with self.app.test_request_context("/"):
            self.middleware.before_request()
            self.assertEqual(request.original_ip, "192.0.2.1")
            self.assertEqual(request.original_port, 54321)
            self.assertEqual(request.nat_type, "Full Cone")

    @patch("conexia.core.STUNClient.get_stun_info", new_callable=AsyncMock, side_effect=Exception("STUN failure"))
    def test_middleware_handles_stun_failure(self, mock_stun):
        """Test middleware behavior when STUN server is unreachable."""
        with self.app.test_request_context("/"):
            self.middleware.before_request()
            self.assertIsNone(request.original_ip)
            self.assertIsNone(request.original_port)
            self.assertIsNone(request.nat_type)

if __name__ == "__main__":
    unittest.main()