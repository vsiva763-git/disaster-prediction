"""
CNN-LSTM Model for Tsunami Prediction
Multi-modal architecture combining spatial and temporal analysis
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from typing import Dict, Tuple, List
from loguru import logger


class TsunamiPredictionModel:
    """
    Multi-modal CNN-LSTM model for tsunami risk prediction
    
    Architecture:
    - CNN layers: Extract spatial-temporal patterns from heterogeneous inputs
    - LSTM layers: Model long-term temporal evolution
    - Dense layers: Final risk classification
    """
    
    def __init__(self, config: Dict):
        """
        Initialize tsunami prediction model
        
        Args:
            config: Model configuration dictionary
        """
        self.config = config['model']
        self.architecture_config = self.config['architecture']
        self.input_config = self.config['input_features']
        self.model = None
        
    def build_model(self, 
                   earthquake_shape: Tuple,
                   ocean_shape: Tuple,
                   spatial_shape: Tuple,
                   temporal_window: int) -> Model:
        """
        Build the complete CNN-LSTM architecture
        
        Args:
            earthquake_shape: Shape of earthquake input features
            ocean_shape: Shape of ocean condition features
            spatial_shape: Shape of spatial/bathymetry features
            temporal_window: Size of temporal window (hours)
            
        Returns:
            Compiled Keras model
        """
        logger.info("Building CNN-LSTM tsunami prediction model...")
        
        # ===== INPUT LAYERS =====
        # Earthquake features: (timesteps, num_earthquakes, features)
        earthquake_input = layers.Input(
            shape=earthquake_shape,
            name='earthquake_input'
        )
        
        # Ocean condition features: (timesteps, num_locations, features)
        ocean_input = layers.Input(
            shape=ocean_shape,
            name='ocean_input'
        )
        
        # Spatial features: (height, width, channels)
        spatial_input = layers.Input(
            shape=spatial_shape,
            name='spatial_input'
        )
        
        # ===== CNN BRANCH FOR SPATIAL FEATURES =====
        spatial_features = self._build_spatial_cnn(spatial_input)
        
        # ===== CNN-LSTM BRANCH FOR EARTHQUAKE DATA =====
        earthquake_features = self._build_temporal_cnn_lstm(
            earthquake_input, 
            name_prefix='earthquake'
        )
        
        # ===== CNN-LSTM BRANCH FOR OCEAN DATA =====
        ocean_features = self._build_temporal_cnn_lstm(
            ocean_input,
            name_prefix='ocean'
        )
        
        # ===== FEATURE FUSION =====
        merged_features = layers.Concatenate(name='feature_fusion')([
            spatial_features,
            earthquake_features,
            ocean_features
        ])
        
        # ===== DENSE LAYERS FOR CLASSIFICATION =====
        x = merged_features
        for i, units in enumerate(self.architecture_config['dense_units']):
            x = layers.Dense(
                units,
                activation='relu',
                name=f'dense_{i+1}'
            )(x)
            x = layers.Dropout(
                self.architecture_config['dropout_rate'],
                name=f'dropout_{i+1}'
            )(x)
        
        # ===== OUTPUT LAYER =====
        # Multi-output: risk probability, confidence, risk class
        risk_probability = layers.Dense(
            1,
            activation='sigmoid',
            name='risk_probability'
        )(x)
        
        confidence_score = layers.Dense(
            1,
            activation='sigmoid',
            name='confidence_score'
        )(x)
        
        risk_class = layers.Dense(
            4,  # 4 classes: none, low, medium, high
            activation='softmax',
            name='risk_class'
        )(x)
        
        # ===== BUILD MODEL =====
        self.model = Model(
            inputs=[earthquake_input, ocean_input, spatial_input],
            outputs=[risk_probability, confidence_score, risk_class],
            name='tsunami_prediction_model'
        )
        
        logger.success("Model architecture built successfully")
        return self.model
    
    def _build_spatial_cnn(self, input_layer) -> layers.Layer:
        """
        Build CNN for spatial/bathymetry features
        
        Args:
            input_layer: Input layer for spatial data
            
        Returns:
            Output layer with extracted spatial features
        """
        x = input_layer
        
        for i, filters in enumerate(self.architecture_config['cnn_filters']):
            x = layers.Conv2D(
                filters=filters,
                kernel_size=self.architecture_config['cnn_kernel_size'][i],
                activation='relu',
                padding='same',
                name=f'spatial_conv_{i+1}'
            )(x)
            x = layers.BatchNormalization(name=f'spatial_bn_{i+1}')(x)
            x = layers.MaxPooling2D(
                pool_size=(2, 2),
                name=f'spatial_pool_{i+1}'
            )(x)
        
        # Global pooling to reduce to vector
        x = layers.GlobalAveragePooling2D(name='spatial_gap')(x)
        
        return x
    
    def _build_temporal_cnn_lstm(self, 
                                 input_layer,
                                 name_prefix: str) -> layers.Layer:
        """
        Build CNN-LSTM for temporal sequence data
        
        Args:
            input_layer: Input layer for temporal data
            name_prefix: Prefix for layer names
            
        Returns:
            Output layer with extracted temporal features
        """
        # Apply 1D CNN to extract patterns across time
        x = layers.Conv1D(
            filters=64,
            kernel_size=3,
            activation='relu',
            padding='same',
            name=f'{name_prefix}_conv1d_1'
        )(input_layer)
        x = layers.BatchNormalization(name=f'{name_prefix}_bn_1')(x)
        
        x = layers.Conv1D(
            filters=128,
            kernel_size=3,
            activation='relu',
            padding='same',
            name=f'{name_prefix}_conv1d_2'
        )(x)
        x = layers.BatchNormalization(name=f'{name_prefix}_bn_2')(x)
        
        # Apply LSTM layers to model temporal evolution
        for i, units in enumerate(self.architecture_config['lstm_units']):
            return_sequences = i < len(self.architecture_config['lstm_units']) - 1
            x = layers.LSTM(
                units,
                return_sequences=return_sequences,
                dropout=self.architecture_config['dropout_rate'],
                name=f'{name_prefix}_lstm_{i+1}'
            )(x)
        
        return x
    
    def compile_model(self, learning_rate: float = None):
        """
        Compile the model with optimizer and loss functions
        
        Args:
            learning_rate: Learning rate (default from config)
        """
        if self.model is None:
            raise ValueError("Model must be built before compilation")
        
        if learning_rate is None:
            learning_rate = self.config['training']['learning_rate']
        
        # Custom loss weights for multi-output
        # Prioritize tsunami detection (risk_probability) over other tasks
        loss_weights = {
            'risk_probability': 5.0,      # Increased to prioritize tsunami detection
            'confidence_score': 0.5,
            'risk_class': 1.0             # Reduced to avoid dominating loss
        }
        
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss={
                'risk_probability': 'binary_crossentropy',
                'confidence_score': 'mse',
                'risk_class': 'categorical_crossentropy'
            },
            loss_weights=loss_weights,
            metrics={
                'risk_probability': ['accuracy', keras.metrics.AUC(name='auc')],
                'confidence_score': ['mae'],
                'risk_class': ['accuracy']
            }
        )
        
        logger.success("Model compiled successfully")
    
    def get_model_summary(self) -> str:
        """
        Get model architecture summary
        
        Returns:
            String representation of model
        """
        if self.model is None:
            return "Model not built yet"
        
        import io
        stream = io.StringIO()
        self.model.summary(print_fn=lambda x: stream.write(x + '\n'))
        return stream.getvalue()
    
    def save_model(self, filepath: str):
        """
        Save model to file
        
        Args:
            filepath: Path to save model
        """
        if self.model is None:
            raise ValueError("No model to save")
        
        self.model.save(filepath)
        logger.success(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """
        Load model from file
        
        Args:
            filepath: Path to load model from
        """
        self.model = keras.models.load_model(filepath)
        logger.success(f"Model loaded from {filepath}")
    
    def predict(self, 
                earthquake_data,
                ocean_data,
                spatial_data) -> Tuple:
        """
        Make predictions using the model
        
        Args:
            earthquake_data: Earthquake input features
            ocean_data: Ocean condition features
            spatial_data: Spatial/bathymetry features
            
        Returns:
            Tuple of (risk_probability, confidence_score, risk_class)
        """
        if self.model is None:
            raise ValueError("Model must be built and loaded before prediction")
        
        predictions = self.model.predict([
            earthquake_data,
            ocean_data,
            spatial_data
        ], verbose=0)
        
        return predictions
