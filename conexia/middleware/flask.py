import asyncio
from flask import request
from conexia.core import STUNClient


class STUNMiddleware:
    def __init__(self, app):
        self.app = app
        self.stun_client = STUNClient(cache_backend="file")
        app.before_request(self.before_request)

    def before_request(self):
        try:
            # Check if the data is cached for request user
            stun_info = asyncio.run(self.stun_client.get_stun_info(request))
            ip = stun_info['data']['ip']
            port = stun_info['data']['port']
            nat_type = stun_info['data']['nat_type']
        except Exception:
            ip, port, nat_type = None, None, None

        # Attach to request object
        request.original_ip = ip
        request.original_port = port
        request.nat_type = nat_type
