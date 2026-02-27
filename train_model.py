"""
Model Training Script
Train the CNN-LSTM tsunami prediction model
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.models import TsunamiPredictionModel, DataPreprocessor, ModelTrainer
from src.utils import setup_logger, load_config, prepare_training_data
from loguru import logger


def main():
    """Main training function"""
    
    parser = argparse.ArgumentParser(
        description='Train Tsunami Prediction Model'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/raw',
        help='Directory with training data'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='models',
        help='Directory to save trained model'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=None,
        help='Number of training epochs (overrides config)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='Batch size (overrides config)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logger(level='INFO')
    
    logger.info("=" * 60)
    logger.info("🤖 TSUNAMI PREDICTION MODEL TRAINING")
    logger.info("=" * 60)
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command-line arguments
    if args.epochs:
        config['model']['training']['epochs'] = args.epochs
    if args.batch_size:
        config['model']['training']['batch_size'] = args.batch_size
    
    # Prepare training data
    logger.info("Preparing training data...")
    prepare_training_data(args.data_dir)
    
    # Initialize components
    logger.info("Initializing model...")
    model = TsunamiPredictionModel(config)
    preprocessor = DataPreprocessor(config)
    trainer = ModelTrainer(config, model, preprocessor)
    
    # Build model architecture
    logger.info("Building model architecture...")
    model.build_model(
        earthquake_shape=(10, 4),  # 10 earthquakes, 4 features
        ocean_shape=(5, 3),        # 5 locations, 3 features
        spatial_shape=(64, 64, 2),  # 64x64 grid, 2 channels
        temporal_window=72
    )
    
    # Compile model
    logger.info("Compiling model...")
    model.compile_model()
    
    # Display model summary
    logger.info("\n" + model.get_model_summary())
    
    # Prepare training data
    logger.info("Loading training data...")
    X_train, y_train, X_val, y_val = trainer.prepare_training_data(args.data_dir)
    
    # Train model
    logger.info("Starting training...")
    history = trainer.train(X_train, y_train, X_val, y_val)
    
    # Save model
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    model_file = output_path / 'best_model.keras'
    model.save_model(str(model_file))
    
    # Save preprocessor scalers
    scaler_dir = output_path / 'scalers'
    preprocessor.save_scalers(str(scaler_dir))
    
    # Plot training history
    plot_file = output_path / 'training_history.png'
    trainer.plot_training_history(str(plot_file))
    
    logger.success("=" * 60)
    logger.success("✅ MODEL TRAINING COMPLETED!")
    logger.success(f"Model saved to: {model_file}")
    logger.success(f"Scalers saved to: {scaler_dir}")
    logger.success(f"Training plot saved to: {plot_file}")
    logger.success("=" * 60)


if __name__ == '__main__':
    main()
