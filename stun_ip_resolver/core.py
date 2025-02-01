import asyncio
import stun
import sqlite3
from stun_ip_resolver.cache import *
from stun_ip_resolver.exceptions import STUNResolutionError


class STUNClient:
    def __init__(self, stun_server="stun.l.google.com", stun_port=19302, cache_backend="memory", **cache_kwargs):
        self.stun_server = stun_server
        self.stun_port = stun_port
        self.cache = IPResolverCache(backend=cache_backend, **cache_kwargs)

    async def get_stun_info(self):
        """Retrieve NAT type, external IP, and external port using configurable caching."""
        try:
            print("Checking cache for STUN info...")
            
            # Check cache for STUN info
            cached_ip = self._get_cached_ips()
            if cached_ip:
                stun_infos = self.cache.get_cached_info(cached_ip[0])  # Fetch first IP stored
                if stun_infos:
                    print("Found STUN info in cache😁")
                    return stun_infos
            
            # If not found in cache, query the STUN server
            print("Fetching new STUN data from server...")
            loop = asyncio.get_running_loop()
            nat_type, ip, port = await loop.run_in_executor(
                None, stun.get_ip_info, "0.0.0.0", 54320, self.stun_server, self.stun_port
            )

            # Save to cache
            stun_infos = {"ip": ip, "port": port, "nat_type": nat_type}
            self.cache.cache_stun_info(ip, port, nat_type)
            return stun_infos

        except Exception as e:
            raise STUNResolutionError(f"Failed to retrieve STUN Info: {e}")


    async def get_public_ip(self):
        stun_info = await self.get_stun_info()
        return stun_info["ip"]

    async def get_public_port(self):
        stun_info = await self.get_stun_info()
        return stun_info["port"]

    async def get_nat_type(self):
        stun_info = await self.get_stun_info()
        return stun_info["nat_type"]

    def _get_cached_ips(self):
        """Retrieve all cached IPs based on backend type."""
        if isinstance(self.cache.cache, (InMemoryCache, FileCache)):
            return list(self.cache.cache.cache.keys())  # Works for dict-like caches
        
        elif isinstance(self.cache.cache, SQLiteCache):
            # Fetch all IPs stored in SQLite
            with sqlite3.connect(self.cache.cache.db_path) as conn:
                cursor = conn.execute("SELECT ip FROM stun_cache")
                return [row[0] for row in cursor.fetchall()]

        elif isinstance(self.cache.cache, RedisCache):
            # Fetch all keys (IPs) stored in Redis
            return self.cache.cache.redis.keys("*")

        return []



# Run async functions properly
async def main():
    client = STUNClient(cache_backend="file")  # Change to "memory", "file", "redis" as needed
    stun_info = await client.get_stun_info()
    print(stun_info)
    print("Public Port:", await client.get_public_port())
    print("NAT Type:", await client.get_nat_type())
    print("Public IP:", await client.get_public_ip())


# Execute
asyncio.run(main())