# **📜 conexia**  

A Python library for fetching and caching a device's real **public IP address** using STUN (Session Traversal Utilities for NAT) servers. Supports **Redis, SQLite, File-based, and In-Memory caching** for fast lookups.

📌 **Why Use This?**  
- Identifies real **public IP address** even behind NAT.  
- Provides **multiple cache backends** (Redis, SQLite, File, Memory).  
- **Works in Django, Flask, or standalone Python scripts**.
- Automatic caching capability with minimal configuration.

---

## **📦 Installation**  

```bash
pip install conexia
```
or install from source:  
```bash
git clone https://github.com/paulsonlegacy/conexia.git
cd conexia
pip install .
```

---

## **⚡ Usage**
### **Basic Example**
```python
from conexia.core import STUNClient

# Choose a backend: "memory", "file", "sqlite", or "redis"
# ttl is time to live in cache in seconds
stun_client = STUNClient(backend="file", ttl=300)

# Retrieve STUN info
stun_info = stun_client.get_stun_info(user_id="device123")
user_id = stun_client.get_user_id()
public_ip = stun_client.get_public_ip()
public_port = stun_client.get_public_port()
nat_type = stun_client.get_nat_type()
print(stun_info)
```

📌 **Output (Example)**  
```json
{
    "user_id": "device123",
    "data": {
        "ip": "192.168.1.10",
        "port": 3478,
        "nat_type": "Full Cone"
    },
    "timestamp": 1691234567
}
```

*NB - User ID is optional as it is automatically generated if not provided*

---

## **🔌 Integrating with Django**

Since Django runs on WSGI by default, you need to enable ASGI for async support in Django.

#### **Using ASGI in Django**

1️⃣ Ensure you have Django 3.2+ installed.  
2️⃣ Create/modify asgi.py in Your Project Root - This file makes Django work asynchronously.


```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")  # Change "your_project"

application = get_asgi_application()
```

NB - The asgi.py file should be in the same folder as settings.py, which is inside your Django project directory (not the root folder with manage.py).

```
your_project/        # Django Project Folder
│── manage.py
│── your_project/    # Actual Django Project Package
│   │── __init__.py
│   │── settings.py
│   │── urls.py
│   │── asgi.py   # ✅ Place asgi.py here!
│   │── wsgi.py
│   └── ...
│── app1/
│── app2/
│── ...
```

3️⃣ Install an ASGI server like daphne or uvicorn:

```python
pip install daphne
```

or

```python
pip install uvicorn
```

4️⃣ Run Django ASGI server:

For daphne:

```python
daphne -b 0.0.0.0 -p 8000 your_project.asgi:application
```

For uvicorn:

```python
uvicorn your_project.asgi:application --host 0.0.0.0 --port 8000
```

5️⃣ Install the package

```bash
pip install conexia
```

6️⃣ Enable the STUN Middleware in settings.py 
Modify settings.py to activate the middleware and configure caching options:

```python
# settings.py
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
    # ✅ Add Conexia Middleware
    "conexia.middleware.django.STUNMiddleware",
]

# STUN Configuration
STUN_CACHE_BACKEND = "sqlite"  # Options: "memory", "file", "sqlite", "redis"
STUN_CACHE_TTL = 300  # Cache expiry in seconds
```

7️⃣ Access STUN data inside Django Views 
Once the middleware is enabled, every request object will have the following attributes: 

```python
def sample_view(request):
    return JsonResponse({
        "original_ip": request.original_ip,
        "original_port": request.original_port,
        "nat_type": request.nat_type
    })
```

---

## **🌐 Integrating with Flask**

Flask does not natively support ASGI, but you can enable async support using hypercorn or uvicorn.

#### Async Support in Flask

1️⃣ Install an ASGI server:

```python
pip install hypercorn
```

or

```python
pip install uvicorn
```

2️⃣ Create app.py

```python
from flask import Flask, jsonify
from conexia.core import STUNClient
import asyncio

app = Flask(__name__)
stun_client = STUNClient(backend="redis", ttl=300)

@app.route("/get_ip/<user_id>")
async def get_ip(user_id):
    stun_info = await asyncio.to_thread(stun_client.get_stun_info, user_id)
    return jsonify(stun_info)

if __name__ == "__main__":
    try:
        import hypercorn.asyncio
        hypercorn.asyncio.serve(app, bind="0.0.0.0:8000")
    except ImportError:
        app.run(debug=True)  # Fallback to sync mode if hypercorn is not installed
```

3️⃣ Choose how to run the server 

Synchronous mode (default Flask WSGI):

```python
python app.py
```

Asynchronous mode (ASGI using hypercorn):

```python
hypercorn app:app --bind 0.0.0.0:8000
```

Alternative ASGI server (uvicorn):

```python
uvicorn app:app --host 0.0.0.0 --port 8000
```

4️⃣ Test API in browser or Postman

```bash
http://127.0.0.1:5000/get_ip/device123
```
### ✅ Alternative Approach Using Flask Hooks 

If you wanted to simulate middleware behavior in Flask, you could use Flask's before_request hook like this:

```python
from flask import Flask, g, request
from conexia.core import STUNClient
import asyncio

app = Flask(__name__)
stun_client = STUNClient(backend="redis", ttl=300)

@app.before_request
async def attach_stun_data():
    user_id = request.args.get("user_id", "default_id")
    stun_info = await asyncio.to_thread(stun_client.get_stun_info, user_id)
    g.stun_info = stun_info  # Attach to global request context

@app.route("/get_ip")
async def get_ip():
    return jsonify(g.stun_info)

if __name__ == "__main__":
    hypercorn.asyncio.serve(app, bind="0.0.0.0:8000")

```

---

## **💾 Available Cache Backends**
| Cache Backend | Description |
|--------------|------------|
| `memory` | Uses in-memory cache (Fast but not persistent). |
| `file` | Saves cached data in `cache.json` (Persistent across restarts). |
| `sqlite` | Uses an SQLite database for efficient storage. |
| `redis` | Uses Redis for distributed caching. |

NB - Default is *file*

---

## **🔧 Clearing Cache**
Clear cache for a specific user ID:  
```python
stun_client.clear_cache(user_id="device123")
```
Clear **all** cached data:  
```python
stun_client.clear_cache()
```

---

## **📜 License**
This project is licensed under the MIT License.

---

## **👨‍💻 Contributing**
1️⃣ **Fork the repository**  
2️⃣ **Clone your fork**  
```bash
git clone https://github.com/paulsonlegacy/conexia.git
cd conexia
```
3️⃣ **Create a feature branch**  
```bash
git checkout -b feature-name
```
4️⃣ **Submit a pull request!** 🚀

---

## **🙌 Acknowledgments**
🎉 **This library is dedicated to my mom - Monica A. Bosah, whose support made this possible.** ❤️ 

---

## **🚀 Next Steps**
- [ ] Add other network parameters in fetched stun info
- [ ] Stand-alone and environment simulated tests for middlewares
- [ ] Support for other python backend frameworks
- [ ] Signalling feature

---

### **💡 Want More Features?**
If you have feature suggestions or bugs, open an issue on **[GitHub](https://github.com/paulsonlegacy/conexia/issues)**! 🚀  
