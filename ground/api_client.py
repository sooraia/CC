import requests

BASE_URL = "http://10.0.1.20:5000"  

def get_active_rovers():
    resp = requests.get(f"{BASE_URL}/rovers/active")
    resp.raise_for_status()
    return resp.json()

def get_last_telemetry():
    resp = requests.get(f"{BASE_URL}/telemetry/last")
    resp.raise_for_status()
    return resp.json()

def get_missions():
    resp = requests.get(f"{BASE_URL}/missions")
    resp.raise_for_status()
    return resp.json()
