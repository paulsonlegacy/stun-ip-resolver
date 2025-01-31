from stun_ip_resolver.core import STUNClient
from stun_ip_resolver.cache import IPResolverCache


class STUNIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.stun_client = STUNClient()
        self.cache = IPResolverCache()

    def __call__(self, request):
        user_id = request.META.get("HTTP_USER_ID")  # Example: Extract user ID from headers
        ip = self.cache.get_cached_ip(user_id)

        if not ip:
            try:
                ip = self.stun_client.get_public_ip()
                self.cache.cache_ip(user_id, ip)
            except Exception:
                ip = None

        request.original_ip = ip  # Attach IP to the request object
        return self.get_response(request)
