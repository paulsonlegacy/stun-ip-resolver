import asyncio
from flask import request
from stun_ip_resolver.core import STUNClient
from stun_ip_resolver.cache import IPResolverCache
from stun_ip_resolver.utils import get_user_id

class STUNIPMiddleware:
    def __init__(self, app):
        self.app = app
        self.stun_client = STUNClient()
        self.cache = IPResolverCache()
        app.before_request(self.before_request)

    def before_request(self):
        # Get the user ID (authenticated user or machine UUID)
        user_id = get_user_id(request)

        # Check if the data is cached
        cached_data = self.cache.get_cached_info(user_id)

        if cached_data:
            ip = cached_data["data"]["ip"]
            port = cached_data["data"]["port"]
            nat_type = cached_data["data"]["nat_type"]
        else:
            try:
                # Fetch IP, Port, and NAT Type from STUN client
                ip, port, nat_type = asyncio.run(self.stun_client.get_stun_info())

                # Cache results
                self.cache.cache_stun_info(user_id, ip, port, nat_type)
            except Exception:
                ip, port, nat_type = None, None, None

        # Attach to request object
        request.original_ip = ip
        request.original_port = port
        request.nat_type = nat_type
