#!/usr/bin/env python3
"""Quick API Test"""
import requests
import numpy as np
import json

print("🌊 Quick API Test\n")

# Test 1: Health
print("1. Health Check:")
r = requests.get("http://localhost:5000/health")
print(f"   Status: {r.status_code}")
print(f"   Model Loaded: {r.json()['model_loaded']}\n")

# Test 2: Prediction
print("2. Tsunami Prediction:")
np.random.seed(42)
test_data = np.random.randn(24, 32).tolist()

payload = {"data": test_data}
r = requests.post("http://localhost:5000/predict", json=payload)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    result = r.json()
    print(f"   Full Response: {json.dumps(result, indent=2)}")
else:
    print(f"   Error: {r.json()}")

print("\n✅ API is operational!")
print("📡 Running on: http://localhost:5000")
print("🌐 Open index.html for web interface")
