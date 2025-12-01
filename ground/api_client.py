import urllib.request
import json

BASE_URL = "http://10.0.12.20:5000"

def get_active_rovers():
    with urllib.request.urlopen(f"{BASE_URL}/rovers/active") as response:
        return json.loads(response.read().decode())

def get_last_telemetry():
    with urllib.request.urlopen(f"{BASE_URL}/telemetry") as response:  # 🔥 removi /last
        return json.loads(response.read().decode())

def get_missions():
    with urllib.request.urlopen(f"{BASE_URL}/missions") as response:
        return json.loads(response.read().decode())