"""
Binary CNN-LSTM Model for Tsunami Prediction with Focal Loss
Simplified architecture focused purely on tsunami detection
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
import keras.backend as K
from typing import Dict, Tuple


def focal_loss(gamma=2.0, alpha=0.25):
    """
    Focal Loss for addressing class imbalance
    Focus on hard negatives and positives
    
    Args:
        gamma: Focusing parameter (higher = more focus on hard examples)
        alpha: Weighting of positive class
    
    Returns:
        Focal loss function
    """
    def focal_loss_fixed(y_true, y_pred):
        # Clip predictions to prevent log(0) - Keras 3 compatible
        epsilon = tf.keras.backend.epsilon()
        y_pred = tf.clip_by_value(y_pred, epsilon, 1. - epsilon)
        
        # Focal loss formula using TensorFlow ops (Keras 3 compatible)
        cross_entropy = -y_true * tf.math.log(y_pred) - (1 - y_true) * tf.math.log(1 - y_pred)
        focal_weight = y_true * alpha * tf.pow(1 - y_pred, gamma) + \
                       (1 - y_true) * (1 - alpha) * tf.pow(y_pred, gamma)
        focal_loss_value = focal_weight * cross_entropy
        
        return tf.reduce_mean(focal_loss_value)
    
    return focal_loss_fixed


class TsunamiPredictionBinaryModel:
    """
    Simplified binary CNN-LSTM model for tsunami detection
    
    Architecture:
    - Single input combining all features
    - CNN-LSTM layers for temporal-spatial analysis
    - Single binary output (tsunami/no-tsunami)
    """
    
    def __init__(self, config: Dict):
        """
        Initialize tsunami prediction model
        
        Args:
            config: Model configuration dictionary
        """
        self.config = config['model']
        self.architecture_config = self.config['architecture']
        self.model = None
        
    def build_model(self, 
                   input_shape: Tuple) -> Model:
        """
        Build simplified binary CNN-LSTM architecture
        
        Args:
            input_shape: Shape of input features (timesteps, features)
            
        Returns:
            Compiled Keras model
        """
        print(f"Building simplified binary CNN-LSTM model with input shape: {input_shape}")
        
        # ===== INPUT LAYER =====
        inputs = layers.Input(shape=input_shape, name='combined_input')
        
        # ===== RESHAPE FOR CNN =====
        # Reshape to (timesteps, features, 1) for 1D CNN
        x = layers.Reshape((input_shape[0], input_shape[1], 1))(inputs)
        
        # ===== CNN BLOCKS FOR FEATURE EXTRACTION =====
        # Block 1: Extract low-level temporal patterns
        x = layers.Conv2D(
            32, (3, 3), activation='relu', padding='same',
            name='conv_1'
        )(x)
        x = layers.MaxPooling2D((2, 2), name='pool_1')(x)
        x = layers.Dropout(0.3, name='dropout_conv_1')(x)
        
        # Block 2: Extract mid-level patterns
        x = layers.Conv2D(
            64, (3, 3), activation='relu', padding='same',
            name='conv_2'
        )(x)
        x = layers.MaxPooling2D((2, 2), name='pool_2')(x)
        x = layers.Dropout(0.3, name='dropout_conv_2')(x)
        
        # ===== LSTM FOR TEMPORAL ANALYSIS =====
        # Reshape for LSTM (samples, timesteps, features)
        x = layers.Reshape((-1, 64))(x)
        
        x = layers.LSTM(
            128, activation='relu', return_sequences=True,
            name='lstm_1'
        )(x)
        x = layers.Dropout(0.3, name='dropout_lstm_1')(x)
        
        x = layers.LSTM(
            64, activation='relu', return_sequences=False,
            name='lstm_2'
        )(x)
        x = layers.Dropout(0.3, name='dropout_lstm_2')(x)
        
        # ===== DENSE LAYERS =====
        x = layers.Dense(128, activation='relu', name='dense_1')(x)
        x = layers.Dropout(0.3, name='dropout_dense_1')(x)
        
        x = layers.Dense(64, activation='relu', name='dense_2')(x)
        x = layers.Dropout(0.2, name='dropout_dense_2')(x)
        
        x = layers.Dense(32, activation='relu', name='dense_3')(x)
        
        # ===== BINARY OUTPUT =====
        outputs = layers.Dense(1, activation='sigmoid', name='tsunami_prediction')(x)
        
        # Create model
        model = Model(inputs=inputs, outputs=outputs, name='TsunamiPredictionBinary')
        
        # ===== COMPILE WITH FOCAL LOSS =====
        # Use focal loss for handling class imbalance
        focal_loss_fn = focal_loss(gamma=2.0, alpha=0.25)
        
        model.compile(
            loss=focal_loss_fn,
            optimizer=keras.optimizers.Adam(learning_rate=0.0005),
            metrics=[
                keras.metrics.BinaryAccuracy(name='accuracy'),
                keras.metrics.AUC(name='auc'),
                keras.metrics.Recall(name='recall'),
                keras.metrics.Precision(name='precision')
            ]
        )
        
        print(f"Model compiled successfully")
        print(f"Parameters: {model.count_params():,}")
        model.summary()
        
        self.model = model
        return model
    
    def get_model(self) -> Model:
        """Get compiled model"""
        return self.model
