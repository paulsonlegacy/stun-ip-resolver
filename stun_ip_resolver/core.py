import asyncio
import stun
from stun_ip_resolver.cache import IPResolverCache
from stun_ip_resolver.exceptions import STUNResolutionError

class STUNClient:
    def __init__(self, stun_server="stun.l.google.com", stun_port=19302):
        self.stun_server = stun_server
        self.stun_port = stun_port
        self.cache = IPResolverCache()  # Initialize cache

    async def get_stun_info(self):
        """Retrieve NAT type, external IP, and external port in one call (async version)"""
        try:
            # Check cache first (based on IP)
            for cached_ip in self.cache.cache.keys():  
                print("Traversing through the cache")
                print(type(self.cache.get_cached_info))
                stun_infos = self.cache.get_cached_info(cached_ip)

                if stun_infos:
                    print("Found stun info in cache..")
                    return stun_infos  # Return cached STUN info
            
            # If not found in cache, query the STUN server
            print("Fetching new STUN data...")
            loop = asyncio.get_running_loop()
            nat_type, ip, port = await loop.run_in_executor(
                None, stun.get_ip_info, "0.0.0.0", self.stun_server, self.stun_port
            )

            # STUN info
            stun_infos = {"ip": ip, "port": port, "nat_type": nat_type}
            # Store STUN info in cache
            self.cache.cache_stun_info(ip, port, nat_type)
            return stun_infos
        except Exception as e:
            raise STUNResolutionError(f"Failed to retrieve STUN Info: {e}")

    async def get_public_ip(self):
        """Returns the public IP assigned by the STUN server"""
        stun_info = await self.get_stun_info()  # Await the async function
        return stun_info["ip"]  
    
    async def get_public_port(self):
        """Returns the public port assigned by the STUN server"""
        stun_info = await self.get_stun_info()
        return stun_info["port"]
    
    async def get_nat_type(self):
        """Returns the NAT type"""
        stun_info = await self.get_stun_info()
        return stun_info["nat_type"]

# Run async functions properly
async def main():
    client = STUNClient()
    stun_info = await client.get_stun_info()
    print(stun_info)
    print("Public Port:", await client.get_public_port())
    print("NAT Type:", await client.get_nat_type())
    print("Public IP:", await client.get_public_ip())

# Execute
asyncio.run(main())