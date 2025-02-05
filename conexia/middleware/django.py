from conexia.core import STUNClient

class STUNIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.stun_client = STUNClient(cache_backend="file")

    async def __call__(self, request):
        try:
            # Fetch STUN info asynchronously
            stun_info = await self.stun_client.get_stun_info(request)
            ip = stun_info['data']['ip']
            port = stun_info['data']['port']
            nat_type = stun_info['data']['nat_type']
        except Exception:
            ip, port, nat_type = None, None, None

        # Attach to request object
        request.original_ip = ip
        request.original_port = port
        request.nat_type = nat_type

        return await self.get_response(request)