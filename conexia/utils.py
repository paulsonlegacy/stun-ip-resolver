import os, uuid

# Constants
CACHE_FILE = os.path.expanduser("~/.stun_resolver_config")
DEFAULT_STUN_SERVERS = [
    {"server":"stun.l.google.com", "port":19302},
    {"server":"stun1.l.google.com", "port":19302},
    {"server":"stun2.l.google.com", "port":19302},
    {"server":"stun3.l.google.com", "port":19302},
    {"server":"stun4.l.google.com", "port":19302},
    # {"server":"stun.stunprotocol.org", "port":3478},
    # {"server":"stun.voipstunt.com", "port":3478},
    # {"server":"stun.sipnet.net", "port":3478},
    # {"server":"stun.twilio.com:3478", "port":3478}
]

# Functions
def get_machine_uuid():
    """Retrieve or create a persistent machine UUID."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return f.read().strip()
    
    new_uuid = str(uuid.uuid4())  # Generate new unique ID
    with open(CACHE_FILE, "w") as f:
        f.write(new_uuid)
    
    return new_uuid


def get_user_id(request):
    """
    Determine whether to use user-based caching or machine-based caching
    """
    if hasattr(request, "user") and request.user.is_authenticated:
        user_id = str(request.user.id)  # Use authenticated user ID
    else:
        user_id = get_machine_uuid()  # Use machine-based UUID for standalone use

    return user_id