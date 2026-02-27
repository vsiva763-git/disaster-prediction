"""
Example Usage Script
Demonstrates how to use the Tsunami Warning System programmatically
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.inference_engine import RealTimeInferenceEngine
from src.utils import setup_logger
from loguru import logger
import time


def example_single_check():
    """Example: Run a single tsunami check"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Single Tsunami Check")
    print("="*60)
    
    # Initialize inference engine
    engine = RealTimeInferenceEngine(
        config_path='config/config.yaml',
        model_path='models/best_model.keras'
    )
    
    # Run single check
    assessment = engine.run_tsunami_check()
    
    if assessment:
        print(f"\n✓ Assessment Complete:")
        print(f"  Alert Level: {assessment['alert_level']}")
        print(f"  India at Risk: {assessment['india_at_risk']}")
        print(f"  Risk Score: {assessment.get('india_risk_score', 0):.3f}")
        print(f"  Message: {assessment['alert_message']}")
        
        if assessment['affected_regions']:
            print(f"  Affected Regions: {', '.join(assessment['affected_regions'])}")
    else:
        print("\n✗ No assessment generated")


def example_continuous_monitoring():
    """Example: Continuous monitoring for 5 minutes"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Continuous Monitoring (5 minutes)")
    print("="*60)
    
    # Initialize inference engine
    engine = RealTimeInferenceEngine()
    
    # Start monitoring with 60-second intervals
    engine.start_monitoring(interval_seconds=60)
    
    print("\n✓ Monitoring started (checking every 60 seconds)")
    print("  Running for 5 minutes...")
    
    try:
        # Monitor for 5 minutes
        for i in range(5):
            time.sleep(60)
            status = engine.get_current_status()
            
            if status['current_assessment']:
                assessment = status['current_assessment']
                print(f"\n  Check {i+1}/5:")
                print(f"    Alert: {assessment['alert_level']}")
                print(f"    Risk: {assessment.get('india_risk_score', 0):.3f}")
            else:
                print(f"\n  Check {i+1}/5: Waiting for first assessment...")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring interrupted by user")
    
    finally:
        # Stop monitoring
        engine.stop_monitoring()
        print("\n✓ Monitoring stopped")


def example_api_interaction():
    """Example: Interact with data collectors directly"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Direct API Interaction")
    print("="*60)
    
    from src.data_collection import USGSEarthquakeCollector
    from src.utils import load_config
    
    # Load config
    config = load_config()
    
    # Initialize USGS collector
    usgs = USGSEarthquakeCollector(config)
    
    # Fetch recent earthquakes
    print("\n✓ Fetching recent earthquakes from USGS...")
    earthquakes = usgs.fetch_recent_earthquakes(hours=24)
    
    if not earthquakes.empty:
        print(f"\n  Found {len(earthquakes)} earthquakes in last 24 hours")
        
        # Show significant ones
        significant = earthquakes[earthquakes['magnitude'] >= 6.5]
        if not significant.empty:
            print(f"\n  Significant earthquakes (M≥6.5): {len(significant)}")
            for idx, eq in significant.iterrows():
                print(f"\n    • M{eq['magnitude']:.1f} - {eq['place']}")
                print(f"      Depth: {eq['depth']:.1f} km")
                print(f"      Location: ({eq['latitude']:.2f}, {eq['longitude']:.2f})")
        else:
            print("\n  No significant earthquakes (M≥6.5)")
    else:
        print("\n  No recent earthquakes found")


def example_model_prediction():
    """Example: Use model for prediction"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Direct Model Prediction")
    print("="*60)
    
    from src.models import TsunamiPredictionModel, DataPreprocessor
    from src.utils import load_config
    import numpy as np
    
    # Load config
    config = load_config()
    
    # Initialize model and preprocessor
    model = TsunamiPredictionModel(config)
    preprocessor = DataPreprocessor(config)
    
    # Build model architecture
    print("\n✓ Building model...")
    model.build_model(
        earthquake_shape=(10, 4),
        ocean_shape=(5, 3),
        spatial_shape=(64, 64, 2),
        temporal_window=72
    )
    
    model.compile_model()
    
    # Create synthetic input data for demonstration
    print("\n✓ Creating synthetic input data...")
    eq_data = np.random.randn(1, 10, 4)
    ocean_data = np.random.randn(1, 5, 3)
    spatial_data = np.random.randn(1, 64, 64, 2)
    
    # Make prediction
    print("\n✓ Running prediction...")
    risk_prob, confidence, risk_class = model.predict(
        eq_data, ocean_data, spatial_data
    )
    
    print(f"\n  Prediction Results:")
    print(f"    Risk Probability: {risk_prob[0][0]:.3f}")
    print(f"    Confidence: {confidence[0][0]:.3f}")
    print(f"    Risk Classes: {risk_class[0]}")
    
    # Interpret risk class
    class_names = ['None', 'Low', 'Medium', 'High']
    predicted_class = np.argmax(risk_class[0])
    print(f"    Predicted Class: {class_names[predicted_class]}")


def example_india_filtering():
    """Example: Test India-specific filtering"""
    print("\n" + "="*60)
    print("EXAMPLE 5: India-Specific Filtering")
    print("="*60)
    
    from src.filtering import IndiaImpactFilter
    from src.utils import load_config
    
    # Load config
    config = load_config()
    
    # Initialize filter
    india_filter = IndiaImpactFilter(config)
    
    # Test earthquake scenarios
    test_scenarios = [
        {
            'name': 'Andaman Sea (High Risk)',
            'earthquake': {
                'latitude': 10.5,
                'longitude': 93.0,
                'magnitude': 7.8,
                'depth': 35.0,
                'time': '2026-01-16T10:00:00'
            },
            'model_prediction': {
                'risk_probability': 0.85,
                'confidence': 0.92,
                'risk_class': [0.0, 0.0, 0.2, 0.8]
            }
        },
        {
            'name': 'Japan (Low Risk to India)',
            'earthquake': {
                'latitude': 35.0,
                'longitude': 140.0,
                'magnitude': 7.5,
                'depth': 40.0,
                'time': '2026-01-16T10:00:00'
            },
            'model_prediction': {
                'risk_probability': 0.75,
                'confidence': 0.88,
                'risk_class': [0.0, 0.1, 0.3, 0.6]
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n  Testing: {scenario['name']}")
        print(f"    Location: ({scenario['earthquake']['latitude']}, "
              f"{scenario['earthquake']['longitude']})")
        print(f"    Magnitude: {scenario['earthquake']['magnitude']}")
        
        result = india_filter.assess_india_risk(
            scenario['earthquake'],
            scenario['model_prediction']
        )
        
        print(f"\n    Result:")
        print(f"      India at Risk: {result['india_at_risk']}")
        print(f"      Risk Score: {result['india_risk_score']:.3f}")
        print(f"      Risk Level: {result['risk_level']}")
        print(f"      Distance: {result.get('distance_to_coast_km', 'N/A')} km")
        
        if result['affected_regions']:
            print(f"      Affected: {', '.join(result['affected_regions'])}")


def main():
    """Run all examples"""
    # Setup logging
    setup_logger(level='INFO')
    
    print("\n" + "="*60)
    print("🌊 TSUNAMI WARNING SYSTEM - USAGE EXAMPLES")
    print("="*60)
    
    try:
        # Run examples
        example_single_check()
        
        # Uncomment to run other examples
        # example_continuous_monitoring()  # Takes 5 minutes
        # example_api_interaction()
        # example_model_prediction()
        # example_india_filtering()
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ EXAMPLES COMPLETED")
    print("="*60)
    print("\nTo run individual examples, uncomment them in main() function")
    print("\nFor more information, see:")
    print("  - README.md for full documentation")
    print("  - API_EXAMPLES.md for API usage")
    print("  - PROJECT_SUMMARY.md for project overview")


if __name__ == '__main__':
    main()
