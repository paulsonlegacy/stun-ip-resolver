import asyncio
from conexia.core import STUNClient


async def main():
    client = STUNClient(cache_backend="file") # Change to "memory", "file", "sqlite", "redis" as needed
    user_id = await client.get_user_id()
    public_ip = await client.get_public_ip()
    public_port = await client.get_public_port()
    nat_type = await client.get_nat_type()
    
    print("User ID:", user_id)
    print("Public IP:", public_ip)
    print("Public Port:", public_port)
    print("NAT Type:", nat_type)

# Execute for CLI only
if __name__ == "__main__":
    asyncio.run(main())

# Run using: python -m conexia.cli