# **📜 Conexio**  

A Python library for fetching and caching a device's real **public IP address** using STUN (Session Traversal Utilities for NAT) servers. Supports **Redis, SQLite, File-based, and In-Memory caching** for fast lookups.

📌 **Why Use This?**  
- Identifies real **public IP address** even behind NAT.  
- Provides **multiple cache backends** (Redis, SQLite, File, Memory).  
- **Works in Django, Flask, or standalone Python scripts**.  

---

## **📦 Installation**  

```bash
pip install conexio
```
or install from source:  
```bash
git clone https://github.com/paulsonlegacy/conexio.git
cd conexio
pip install .
```

---

## **⚡ Usage**
### **Basic Example**
```python
from conexio import IPResolverCache

# Choose a backend: "memory", "file", "sqlite", or "redis"
cache = IPResolverCache(backend="file", ttl=300)

# Store STUN info
cache.cache_stun_info(user_id="device123", ip="192.168.1.10", port=3478, nat_type="Full Cone", timestamp=1691234567)

# Retrieve STUN info
stun_info = cache.get_stun_info(user_id="device123")
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

NB - User ID is optional as it is automatically generated if not provided
---

## **🔌 Integrating with Django**
1️⃣ **Install the package**  
```bash
pip install conexio
```
2️⃣ **Modify `settings.py`**  
```python
# settings.py
STUN_CACHE_BACKEND = "sqlite"  # Options: "memory", "file", "sqlite", "redis"
STUN_CACHE_TTL = 300  # Cache expiry in seconds
```

3️⃣ **Use in Django Views**  
```python
from django.http import JsonResponse
from conexio import IPResolverCache

cache = IPResolverCache(backend="sqlite", ttl=300)

def get_ip(request):
    user_id = str(request.user.id)  # Get unique user ID
    stun_info = cache.get_stun_info(user_id)
    return JsonResponse(stun_info)
```

---

## **🌐 Integrating with Flask**
1️⃣ **Install the package**  
```bash
pip install conexio
```

2️⃣ **Create `app.py`**
```python
from flask import Flask, jsonify
from conexio import IPResolverCache

app = Flask(__name__)
cache = IPResolverCache(backend="redis", ttl=300)

@app.route("/get_ip/<user_id>")
def get_ip(user_id):
    stun_info = cache.get_stun_info(user_id)
    return jsonify(stun_info)

if __name__ == "__main__":
    app.run(debug=True)
```
3️⃣ **Run the server**  
```bash
python app.py
```

4️⃣ **Test API in browser or Postman**  
```
http://127.0.0.1:5000/get_ip/device123
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
cache.clear_cache(user_id="device123")
```
Clear **all** cached data:  
```python
cache.clear_cache()
```

---

## **📜 License**
This project is licensed under the MIT License.

---

## **👨‍💻 Contributing**
1️⃣ **Fork the repository**  
2️⃣ **Clone your fork**  
```bash
git clone https://github.com/paulsonlegacy/conexio.git
cd conexio
```
3️⃣ **Create a feature branch**  
```bash
git checkout -b feature-name
```
4️⃣ **Submit a pull request!** 🚀

---

## **🙌 Acknowledgments**
🎉 **This library is dedicated to my mom - Monica Bosah, whose support made this possible.** ❤️  

---

## **🚀 Next Steps**
- [ ] Add CLI tool for checking STUN info  
- [ ] Improve performance for large-scale use  

---

### **📌 Final Steps Before Uploading to PyPI**
✅ **Ensure `setup.py` is correct**  
✅ **Run tests**  
✅ **Upload package**  
```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

---

### **💡 Want More Features?**
If you have feature suggestions or bugs, open an issue on **[GitHub](https://github.com/paulsonlegacy/conexio/issues)**! 🚀  
