"""
Model Trainer
Handles model training with global tsunami dataset
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional
import tensorflow as tf
from tensorflow import keras

from .cnn_lstm_binary_model import TsunamiPredictionBinaryModel
from .data_preprocessor import DataPreprocessor


class ModelTrainer:
    """Trains tsunami prediction model on global historical data"""
    
    def __init__(self, config: Dict, model: TsunamiPredictionBinaryModel, 
                 preprocessor: DataPreprocessor):
        """
        Initialize model trainer
        
        Args:
            config: Configuration dictionary
            model: TsunamiPredictionBinaryModel instance
            preprocessor: DataPreprocessor instance
        """
        self.config = config['model']
        self.training_config = self.config['training']
        self.model = model
        self.preprocessor = preprocessor
        self.history = None
    
    def prepare_training_data(self, data_dir: str) -> Tuple:
        """
        Prepare training data from global tsunami database
        
        Args:
            data_dir: Directory containing training data
            
        Returns:
            Tuple of (X_train, y_train, X_val, y_val)
        """
        print("Preparing training data from global tsunami database...")
        
        data_path = Path(data_dir)
        
        # Load global tsunami events dataset
        # Format: CSV with columns [event_id, date, latitude, longitude, 
        #         magnitude, depth, tsunami_occurred, intensity, ...]
        
        tsunami_events_file = data_path / 'global_tsunami_events.csv'
        
        if not tsunami_events_file.exists():
            print("Global tsunami dataset not found. Creating sample data...")
            return self._create_sample_training_data()
        
        df = pd.read_csv(tsunami_events_file)
        print(f"Loaded {len(df)} tsunami events")
        
        # Process each event
        X_earthquake = []
        X_ocean = []
        X_spatial = []
        y_risk_prob = []
        y_confidence = []
        y_risk_class = []
        
        for idx, row in df.iterrows():
            # For each event, we would load associated earthquake and ocean data
            # This is a simplified version
            
            # Create dummy data for demonstration
            eq_data = np.random.randn(1, 10, 4)
            ocean_data = np.random.randn(1, 5, 3)
            spatial_data = np.random.randn(64, 64, 2)
            
            # Labels
            tsunami_occurred = row.get('tsunami_occurred', False)
            intensity = row.get('intensity', 'none')
            
            risk_prob, confidence, risk_class = self.preprocessor.create_training_labels(
                tsunami_occurred, intensity
            )
            
            X_earthquake.append(eq_data)
            X_ocean.append(ocean_data)
            X_spatial.append(spatial_data)
            y_risk_prob.append(risk_prob)
            y_confidence.append(confidence)
            y_risk_class.append(risk_class)
        
        # Convert to arrays
        X_earthquake = np.vstack(X_earthquake)
        X_ocean = np.vstack(X_ocean)
        X_spatial = np.array(X_spatial)
        y_risk_prob = np.vstack(y_risk_prob)
        y_confidence = np.vstack(y_confidence)
        y_risk_class = np.vstack(y_risk_class)
        
        # Split into train/validation
        val_split = self.training_config['validation_split']
        val_size = int(len(X_earthquake) * val_split)
        
        X_train = [
            X_earthquake[val_size:],
            X_ocean[val_size:],
            X_spatial[val_size:]
        ]
        y_train = [
            y_risk_prob[val_size:],
            y_confidence[val_size:],
            y_risk_class[val_size:]
        ]
        
        X_val = [
            X_earthquake[:val_size],
            X_ocean[:val_size],
            X_spatial[:val_size]
        ]
        y_val = [
            y_risk_prob[:val_size],
            y_confidence[:val_size],
            y_risk_class[:val_size]
        ]
        
        print(f"Training data prepared: {len(X_train[0])} train, {len(X_val[0])} validation")
        
        return X_train, y_train, X_val, y_val
    
    def _create_sample_training_data(self) -> Tuple:
        """Create sample training data for demonstration"""
        print("Creating synthetic training data for demonstration")
        
        n_samples = 1000
        
        X_earthquake = np.random.randn(n_samples, 10, 4)
        X_ocean = np.random.randn(n_samples, 5, 3)
        X_spatial = np.random.randn(n_samples, 64, 64, 2)
        
        # Create labels with class imbalance (tsunamis are rare)
        tsunami_prob = np.random.choice([0, 1], size=n_samples, p=[0.95, 0.05])
        y_risk_prob = tsunami_prob.reshape(-1, 1)
        y_confidence = np.random.uniform(0.7, 1.0, size=(n_samples, 1))
        
        # Risk class (one-hot encoded)
        y_risk_class = np.zeros((n_samples, 4))
        for i in range(n_samples):
            if tsunami_prob[i] == 0:
                y_risk_class[i, 0] = 1  # none
            else:
                class_idx = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
                y_risk_class[i, class_idx] = 1
        
        # Split
        val_split = self.training_config['validation_split']
        val_size = int(n_samples * val_split)
        
        X_train = [X_earthquake[val_size:], X_ocean[val_size:], X_spatial[val_size:]]
        y_train = [y_risk_prob[val_size:], y_confidence[val_size:], y_risk_class[val_size:]]
        
        X_val = [X_earthquake[:val_size], X_ocean[:val_size], X_spatial[:val_size]]
        y_val = [y_risk_prob[:val_size], y_confidence[:val_size], y_risk_class[:val_size]]
        
        return X_train, y_train, X_val, y_val
    
    def train(self, X_train, y_train, X_val, y_val, 
              checkpoint_dir: str = 'models/checkpoints',
              sample_weights: Optional[np.ndarray] = None) -> keras.callbacks.History:
        """
        Train the model with Focal Loss (binary model)
        
        Args:
            X_train: Training inputs (1D array of shape)
            y_train: Training labels (binary)
            X_val: Validation inputs
            y_val: Validation labels (binary)
            checkpoint_dir: Directory for saving checkpoints
            sample_weights: Optional sample weights for handling imbalance (works with focal loss)
            
        Returns:
            Training history
        """
        print("Starting model training with Focal Loss...")
        
        # Create checkpoint directory
        Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
        
        # Setup callbacks
        callbacks = self._setup_callbacks(checkpoint_dir)
        
        # Train model with sample weights (compatible with multi-task and focal loss)
        train_kwargs = {
            'x': X_train,
            'y': y_train,
            'batch_size': self.training_config['batch_size'],
            'epochs': self.training_config['epochs'],
            'validation_data': (X_val, y_val),
            'callbacks': callbacks,
            'verbose': 1
        }
        
        if sample_weights is not None:
            train_kwargs['sample_weight'] = sample_weights
            print(f"Using sample weights: min={sample_weights.min():.3f}, max={sample_weights.max():.3f}, mean={sample_weights.mean():.3f}")
        
        self.history = self.model.model.fit(**train_kwargs)
        
        print("Model training completed!")
        
        return self.history
    
    def _setup_callbacks(self, checkpoint_dir: str) -> list:
        """Setup training callbacks"""
        callbacks = []
        
        # Model checkpoint
        checkpoint_path = Path(checkpoint_dir) / 'best_model.keras'
        callbacks.append(
            keras.callbacks.ModelCheckpoint(
                filepath=str(checkpoint_path),
                monitor='val_loss',
                save_best_only=True,
                save_weights_only=False,
                verbose=1
            )
        )
        
        # Early stopping
        callbacks.append(
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=self.training_config['early_stopping_patience'],
                restore_best_weights=True,
                verbose=1
            )
        )
        
        # Reduce learning rate on plateau
        callbacks.append(
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=self.training_config['reduce_lr_patience'],
                min_lr=1e-7,
                verbose=1
            )
        )
        
        # TensorBoard logging
        log_dir = Path('logs') / 'tensorboard'
        log_dir.mkdir(parents=True, exist_ok=True)
        callbacks.append(
            keras.callbacks.TensorBoard(
                log_dir=str(log_dir),
                histogram_freq=1,
                write_graph=True
            )
        )
        
        # CSV logger
        csv_log_path = Path('logs') / 'training_log.csv'
        callbacks.append(
            keras.callbacks.CSVLogger(
                str(csv_log_path),
                append=True
            )
        )
        
        return callbacks
    
    def evaluate(self, X_test, y_test) -> Dict:
        """
        Evaluate model on test data
        
        Args:
            X_test: Test inputs
            y_test: Test labels
            
        Returns:
            Dictionary of evaluation metrics
        """
        print("Evaluating model...")
        
        results = self.model.model.evaluate(X_test, y_test, verbose=0)
        
        # Parse results
        metrics = {}
        for i, metric_name in enumerate(self.model.model.metrics_names):
            metrics[metric_name] = results[i]
        
        print("Model evaluation completed")
        
        return metrics
    
    def plot_training_history(self, save_path: Optional[str] = None):
        """
        Plot training history
        
        Args:
            save_path: Optional path to save plot
        """
        if self.history is None:
            print("No training history available")
            return
        
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Loss
        axes[0, 0].plot(self.history.history['loss'], label='Train Loss')
        axes[0, 0].plot(self.history.history['val_loss'], label='Val Loss')
        axes[0, 0].set_title('Model Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Risk probability accuracy
        if 'risk_probability_accuracy' in self.history.history:
            axes[0, 1].plot(self.history.history['risk_probability_accuracy'], 
                          label='Train Accuracy')
            axes[0, 1].plot(self.history.history['val_risk_probability_accuracy'], 
                          label='Val Accuracy')
            axes[0, 1].set_title('Risk Probability Accuracy')
            axes[0, 1].set_xlabel('Epoch')
            axes[0, 1].set_ylabel('Accuracy')
            axes[0, 1].legend()
            axes[0, 1].grid(True)
        
        # AUC
        if 'risk_probability_auc' in self.history.history:
            axes[1, 0].plot(self.history.history['risk_probability_auc'], 
                          label='Train AUC')
            axes[1, 0].plot(self.history.history['val_risk_probability_auc'], 
                          label='Val AUC')
            axes[1, 0].set_title('Risk Probability AUC')
            axes[1, 0].set_xlabel('Epoch')
            axes[1, 0].set_ylabel('AUC')
            axes[1, 0].legend()
            axes[1, 0].grid(True)
        
        # Risk class accuracy
        if 'risk_class_accuracy' in self.history.history:
            axes[1, 1].plot(self.history.history['risk_class_accuracy'], 
                          label='Train Accuracy')
            axes[1, 1].plot(self.history.history['val_risk_class_accuracy'], 
                          label='Val Accuracy')
            axes[1, 1].set_title('Risk Class Accuracy')
            axes[1, 1].set_xlabel('Epoch')
            axes[1, 1].set_ylabel('Accuracy')
            axes[1, 1].legend()
            axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Training history plot saved to {save_path}")
        else:
            plt.show()
