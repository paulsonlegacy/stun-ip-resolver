import asyncio, stun, sqlite3, time, random
from conexia.cache import *
from conexia.exceptions import STUNResolutionError
from conexia.utils import get_user_id
from conexia.utils import DEFAULT_STUN_SERVERS


class STUNClient:
    def __init__(self, stun_server=None, stun_port=None, cache_backend="file", ttl=300, **cache_kwargs): #TTL is in seconds
        """Initialize STUN client with caching support."""
        server_count = random.randint(0, len(DEFAULT_STUN_SERVERS) - 1)
        self.stun_server = stun_server or DEFAULT_STUN_SERVERS[server_count]["server"]
        self.stun_port = int(stun_port or DEFAULT_STUN_SERVERS[server_count]["port"])
        self.cache = IPResolverCache(backend=cache_backend, ttl=ttl, **cache_kwargs)
        print(f"Using STUN Server: {self.stun_server}, Port: {self.stun_port}")  # Debugging output

    def _get_cached_ips(self):
        """Retrieve all cached IPs based on backend type."""
        if isinstance(self.cache.cache, InMemoryCache):
            return list(self.cache.cache.cache.keys())  # Works for dict-like caches

        elif isinstance(self.cache.cache, FileCache):
            cache_data = self.cache.cache._load_cache()  # Load JSON file data
            return list(cache_data.keys())  # Return IPs stored in the file

        elif isinstance(self.cache.cache, SQLiteCache):
            with sqlite3.connect(self.cache.cache.db_path) as conn:
                cursor = conn.execute("SELECT ip FROM stun_cache")
                return [row[0] for row in cursor.fetchall()]  # Extract IPs

        elif isinstance(self.cache.cache, RedisCache):
            return self.cache.cache.redis.keys("*")  # Fetch all Redis keys

        return []

    async def get_stun_info(self, request=None):
        """Retrieve NAT type, external IP, and external port using configurable caching."""

        timestamp = time.time()  # Current timestamp

        try:
            print("Checking cache for STUN info...")
            
            # Determine user ID (web app users get request.user.id, CLI users get machine UUID)
            user_id = get_user_id(request)

            # Check cache for STUN info
            cached_ip = self._get_cached_ips()
            if cached_ip:
                stun_infos = self.cache.get_cached_info(user_id)
                if stun_infos:
                    print("Found STUN info in cache")
                    return stun_infos
            
            # If not found in cache, query the STUN server
            print("Fetching new STUN data from server...")
            loop = asyncio.get_running_loop()
            nat_type, ip, port = await loop.run_in_executor(
                None, stun.get_ip_info, "0.0.0.0", 54320, self.stun_server, self.stun_port
            )
            # Save to cache
            self.cache.cache_stun_info(user_id, ip, port, nat_type, timestamp)
            
            # Stun info dictionary
            stun_infos = {
                "user_id": user_id,
                "data": {"ip": ip, "port": port, "nat_type": nat_type}, 
                "timestamp": timestamp
            }
            return stun_infos

        except Exception as e:
            raise STUNResolutionError(f"Failed to retrieve STUN Info: {e}")


    async def get_user_id(self, request=None):
        stun_info = await self.get_stun_info(request)
        return stun_info["user_id"]
    
    async def get_public_ip(self, request=None):
        stun_info = await self.get_stun_info(request)
        return stun_info["data"]["ip"]

    async def get_public_port(self, request=None):
        stun_info = await self.get_stun_info(request)
        return stun_info["data"]["port"]

    async def get_nat_type(self, request=None):
        stun_info = await self.get_stun_info(request)
        return stun_info["data"]["nat_type"]