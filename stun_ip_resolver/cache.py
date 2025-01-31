from cachetools import LRUCache



class IPResolverCache:
    def __init__(self, max_size=100):
        self.cache = LRUCache(maxsize=max_size)

    def get_cached_info(self, ip):
        """Retrieve cached STUN info for a given IP."""
        return self.cache.get(ip, None)  # Returns full STUN info if available

    def cache_stun_info(self, ip, port, nat_type):
        """Cache the resolved STUN info."""
        self.cache[ip] = {
            "ip": ip,
            "port": port,
            "nat_type": nat_type
        }

    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()
