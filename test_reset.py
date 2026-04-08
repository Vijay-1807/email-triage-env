import json
import urllib.request

BASE = 'http://localhost:7860'

def test_endpoint(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {'Content-Type': 'application/json'} if data else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode())
        print(f"✅ {method} {path} -> {json.dumps(result, indent=2)[:300]}")
        return result
    except Exception as e:
        body_text = e.read().decode() if hasattr(e, 'read') else str(e)
        print(f"❌ {method} {path} -> {body_text}")
        return None

print("=== Testing all endpoints ===\n")

# 1. Health
test_endpoint("GET", "/health")

# 2. Reset
test_endpoint("POST", "/reset", {})

# 3. State
test_endpoint("GET", "/state")

# 4. Step
test_endpoint("POST", "/step", {
    "action": {
        "department": "billing",
        "action": "resolve",
        "confidence": 0.8
    }
})

# 5. State after step
test_endpoint("GET", "/state")

print("\n=== All endpoint tests complete ===")
