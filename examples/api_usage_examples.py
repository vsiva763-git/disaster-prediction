#!/usr/bin/env python3
"""
Complete API Usage Examples for Tsunami Detection Model
"""

import requests
import numpy as np
import json
from typing import List, Dict, Any

API_BASE_URL = "http://localhost:5000"

# ============================================================================
# Example 1: Health Check
# ============================================================================

def check_api_health():
    """Verify API is running and model is loaded"""
    response = requests.get(f"{API_BASE_URL}/health")
    print("Health Status:", response.json())
    return response.json()


# ============================================================================
# Example 2: Get Model Information
# ============================================================================

def get_model_info():
    """Retrieve model configuration and performance metrics"""
    response = requests.get(f"{API_BASE_URL}/model-info")
    metadata = response.json()
    
    print("\n=== Model Information ===")
    print(f"Model Type: {metadata['model']['model_type']}")
    print(f"Input Shape: {metadata['model']['input_shape']}")
    print(f"Validation AUC: {metadata['model']['validation_auc']:.4f}")
    print(f"Test Accuracy: {metadata['model']['test_auc']:.4f}")
    print(f"Optimal Threshold: {metadata['model']['threshold']}")
    
    return metadata


# ============================================================================
# Example 3: Single Sample Prediction
# ============================================================================

def predict_single_sample(threshold: float = 0.1) -> Dict[str, Any]:
    """
    Make prediction for a single 24×32 sample
    
    Args:
        threshold: Decision threshold (0.1 for maximum safety)
    
    Returns:
        Prediction result with probability and alert status
    """
    # Generate sample data (24 timesteps, 32 features)
    sample_data = np.random.randn(24, 32).tolist()
    
    # Make request
    response = requests.post(
        f"{API_BASE_URL}/predict",
        json={
            "data": sample_data,
            "threshold": threshold
        }
    )
    
    result = response.json()
    
    print("\n=== Single Prediction ===")
    print(f"Probability: {result['probabilities'][0]:.4f}")
    print(f"Threshold: {result['threshold']}")
    print(f"Alert Triggered: {bool(result['alerts'][0])}")
    print(f"Interpretation: {result['interpretation'][0]}")
    
    return result


# ============================================================================
# Example 4: Simulated Tsunami Detection
# ============================================================================

def simulate_tsunami_detection(threshold: float = 0.1) -> Dict[str, Any]:
    """
    Simulate detection of tsunami pattern
    
    Tsunami patterns typically have:
    - Higher amplitude seismic waves
    - Specific frequency signatures
    - Temporal correlations
    """
    # Create data with tsunami-like pattern (higher amplitude)
    tsunami_data = (np.random.randn(24, 32) * 1.5).tolist()
    
    response = requests.post(
        f"{API_BASE_URL}/predict",
        json={
            "data": tsunami_data,
            "threshold": threshold
        }
    )
    
    result = response.json()
    
    print("\n=== Simulated Tsunami Pattern ===")
    print(f"Probability: {result['probabilities'][0]:.4f}")
    print(f"Alert Triggered: {bool(result['alerts'][0])}")
    if result['alerts'][0]:
        print("🚨 TSUNAMI ALERT TRIGGERED!")
    else:
        print("✓ No tsunami detected")
    
    return result


# ============================================================================
# Example 5: Batch Predictions
# ============================================================================

def batch_predict(n_samples: int = 10, threshold: float = 0.1) -> Dict[str, Any]:
    """
    Make predictions for multiple samples in a single request
    
    More efficient for processing multiple data points
    
    Args:
        n_samples: Number of samples to process
        threshold: Decision threshold
    
    Returns:
        Batch results with alert counts
    """
    # Generate batch data
    batch_data = [
        np.random.randn(24, 32).tolist() 
        for _ in range(n_samples)
    ]
    
    response = requests.post(
        f"{API_BASE_URL}/batch-predict",
        json={
            "samples": batch_data,
            "threshold": threshold
        }
    )
    
    result = response.json()
    
    print(f"\n=== Batch Prediction ({n_samples} samples) ===")
    print(f"Alert Count: {result['alert_count']}")
    print(f"Alert Rate: {result['alert_rate']}")
    print(f"Probabilities (first 5): {[f'{p:.4f}' for p in result['probabilities'][:5]]}")
    
    return result


# ============================================================================
# Example 6: Different Threshold Strategies
# ============================================================================

def test_thresholds():
    """
    Test different threshold values to understand trade-offs
    
    Thresholds:
    - 0.1: Maximum sensitivity (catches all tsunamis, possible false alarms)
    - 0.5: Balanced (default)
    - 0.7: Conservative (fewer false alarms, might miss some events)
    """
    sample_data = np.random.randn(24, 32).tolist()
    
    print("\n=== Threshold Testing ===")
    
    thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]
    
    for threshold in thresholds:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={
                "data": sample_data,
                "threshold": threshold
            }
        )
        
        result = response.json()
        prob = result['probabilities'][0]
        alert = bool(result['alerts'][0])
        
        print(f"Threshold {threshold}: Probability={prob:.4f}, Alert={alert}")


# ============================================================================
# Example 7: Real-world Integration (Simulated)
# ============================================================================

def simulate_real_data_pipeline():
    """
    Simulate integration with real seismic and ocean data pipeline
    """
    print("\n=== Real-world Data Pipeline Simulation ===")
    
    # Simulated functions (would be replaced with actual data sources)
    def fetch_seismic_data():
        """Fetch from USGS seismic network"""
        return np.random.randn(24, 16).tolist()
    
    def fetch_ocean_data():
        """Fetch from NOAA ocean monitoring"""
        return np.random.randn(24, 16).tolist()
    
    # Fetch data
    seismic = np.array(fetch_seismic_data())
    ocean = np.array(fetch_ocean_data())
    
    # Combine features (24 timesteps, 32 features)
    combined = np.hstack([seismic, ocean]).tolist()
    
    # Make prediction
    response = requests.post(
        f"{API_BASE_URL}/predict",
        json={
            "data": combined,
            "threshold": 0.1  # Maximum sensitivity for early warning
        }
    )
    
    result = response.json()
    
    if result['alerts'][0]:
        print("⚠️  TSUNAMI ALERT ISSUED")
        print(f"   Probability: {result['probabilities'][0]:.4f}")
        print("   Actions:")
        print("   - Notify coastal communities")
        print("   - Activate siren systems")
        print("   - Deploy emergency response")
    else:
        print("✓ No tsunami threat detected")


# ============================================================================
# Example 8: Error Handling
# ============================================================================

def demonstrate_error_handling():
    """Show how to handle various error scenarios"""
    print("\n=== Error Handling Examples ===")
    
    # Error 1: Invalid input shape
    print("\n1. Invalid input shape:")
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"data": [[1, 2, 3]]}  # Wrong shape
        )
        if not response.json().get('success'):
            print(f"   Error: {response.json()['error']}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Error 2: Missing data field
    print("\n2. Missing required field:")
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"threshold": 0.5}  # Missing "data"
        )
        if not response.json().get('success'):
            print(f"   Error: {response.json()['error']}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Error 3: Connection error
    print("\n3. Connection handling:")
    try:
        response = requests.post(
            "http://invalid-host:5000/predict",
            json={"data": np.random.randn(24, 32).tolist()}
        )
    except requests.exceptions.ConnectionError as e:
        print(f"   Connection Error (API not available): {str(e)[:50]}...")


# ============================================================================
# Main Example Runner
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TSUNAMI DETECTION API - USAGE EXAMPLES")
    print("=" * 60)
    
    try:
        # Check if API is running
        health = check_api_health()
        if not health.get('model_loaded'):
            print("\n⚠️  Warning: Model not loaded on server")
            exit(1)
        
        # Run examples
        get_model_info()
        predict_single_sample()
        simulate_tsunami_detection()
        batch_predict(n_samples=5)
        test_thresholds()
        simulate_real_data_pipeline()
        demonstrate_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API")
        print("   Make sure the API server is running:")
        print("   $ python app.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
