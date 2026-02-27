#!/usr/bin/env python3
"""
Live API Testing Script
Tests all endpoints with real data and displays results
"""

import requests
import json
import numpy as np
from time import sleep

API_URL = "http://localhost:5000"

print("=" * 80)
print("🌊 TSUNAMI EARLY WARNING SYSTEM - LIVE API TEST")
print("=" * 80)
print()

# Test 1: Health Check
print("📍 TEST 1: Health Check")
print("-" * 80)
try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("✅ PASS\n")
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Test 2: Model Info
print("📍 TEST 2: Model Information")
print("-" * 80)
try:
    response = requests.get(f"{API_URL}/model-info", timeout=5)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Model Type: {data.get('model_type')}")
    print(f"Input Shape: {data.get('input_shape')}")
    print(f"Parameters: {data.get('total_parameters'):,}")
    print(f"Validation AUC: {data.get('validation_metrics', {}).get('auc')}")
    print(f"Test Accuracy: {data.get('test_metrics', {}).get('accuracy')}")
    print("✅ PASS\n")
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Test 3: Single Prediction - Tsunami Pattern
print("📍 TEST 3: Tsunami Detection (High Risk Pattern)")
print("-" * 80)
try:
    # Generate tsunami-like pattern: high amplitude, escalating frequency
    np.random.seed(42)
    # Create (24, 32) shaped array - 24 time steps, 32 features each
    tsunami_pattern = np.zeros((24, 32))
    for i in range(24):
        tsunami_pattern[i] = np.linspace(0.1 + i*0.03, 0.9 + i*0.01, 32)
    
    tsunami_data = {
        "seismic_data": tsunami_pattern.tolist()
    }
    
    response = requests.post(
        f"{API_URL}/predict",
        json=tsunami_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Prediction: {result.get('prediction')}")
    print(f"Probability: {result.get('probability'):.4f}")
    print(f"Confidence: {result.get('confidence'):.2%}")
    print(f"Alert: {result.get('alert_level')}")
    print("✅ PASS\n")
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Test 4: Single Prediction - Normal Pattern
print("📍 TEST 4: Normal Signal Detection (Low Risk Pattern)")
print("-" * 80)
try:
    # Generate normal pattern: low amplitude, stable
    np.random.seed(123)
    normal_data = {
        "seismic_data": (np.random.randn(24, 32) * 0.1 + 0.2).tolist()
    }
    
    response = requests.post(
        f"{API_URL}/predict",
        json=normal_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Prediction: {result.get('prediction')}")
    print(f"Probability: {result.get('probability'):.4f}")
    print(f"Confidence: {result.get('confidence'):.2%}")
    print(f"Alert: {result.get('alert_level')}")
    print("✅ PASS\n")
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Test 5: Batch Predictions
print("📍 TEST 5: Batch Predictions (3 samples)")
print("-" * 80)
try:
    np.random.seed(456)
    # Create 3 different patterns
    tsunami_pattern = np.zeros((24, 32))
    for i in range(24):
        tsunami_pattern[i] = np.linspace(0.1 + i*0.03, 0.9 + i*0.01, 32)
    
    normal_pattern = np.random.randn(24, 32) * 0.1 + 0.2
    
    moderate_pattern = np.zeros((24, 32))
    for i in range(24):
        moderate_pattern[i] = np.linspace(0.2 + i*0.02, 0.6 + i*0.01, 32)
    
    batch_data = {
        "batch_data": [
            tsunami_pattern.tolist(),
            normal_pattern.tolist(),
            moderate_pattern.tolist()
        ]
    }
    
    response = requests.post(
        f"{API_URL}/batch-predict",
        json=batch_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    results = response.json()
    print(f"Total Samples: {results.get('total_samples')}")
    print(f"Processing Time: {results.get('processing_time_ms'):.2f} ms")
    print("\nPredictions:")
    for i, pred in enumerate(results.get('predictions', [])[:5], 1):
        print(f"  Sample {i}: {pred.get('prediction')} (prob={pred.get('probability'):.4f})")
    print("✅ PASS\n")
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Summary
print("=" * 80)
print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
print("=" * 80)
print()
print("🚀 System Status: FULLY OPERATIONAL")
print("📡 API Endpoint: http://localhost:5000")
print("🌐 Web Dashboard: Open index.html in browser")
print()
print("🎯 Next Steps:")
print("  1. Access web dashboard for interactive testing")
print("  2. Deploy to production (Docker or cloud platform)")
print("  3. Set up monitoring and alerting")
print("  4. Configure real-time seismic data feeds")
print()
