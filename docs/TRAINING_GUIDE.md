# Model Training Guide

This guide covers different methods to train the tsunami prediction model.

## 🎯 Training Options

### Option 1: Google Colab (Recommended) 🚀

**Advantages:**
- Free GPU/TPU access
- No local setup required
- Pre-configured environment
- Easy to share and reproduce
- Can train larger models faster

**Steps:**

1. **Open the Colab Notebook:**
   - Go to [Google Colab](https://colab.research.google.com/)
   - Click `File → Open notebook → GitHub`
   - Enter: `vsiva763-git/India-specific-tsunami-early-warning-system`
   - Select: `Train_Tsunami_Model_Colab.ipynb`

2. **Set Runtime to GPU:**
   - Click `Runtime → Change runtime type`
   - Select `Hardware accelerator: GPU` (T4 or better)
   - Click `Save`

3. **Run All Cells:**
   - Click `Runtime → Run all`
   - Or run cells one by one (Shift+Enter)

4. **Monitor Training:**
   - Watch the loss and accuracy metrics
   - Training typically takes 15-30 minutes for 50 epochs

5. **Download Model:**
   - The last cell downloads `tsunami_model.zip`
   - Extract and copy to your project's `models/` directory

**Colab Training Parameters:**
```python
epochs = 50              # Adjust based on convergence
batch_size = 64         # Larger for GPU
learning_rate = 0.001   # Default
```

### Option 2: Local Training 💻

**Advantages:**
- Full control over environment
- No internet dependency during training
- Can use local datasets
- Direct integration with project

**Requirements:**
- Python 3.8+
- TensorFlow 2.18 (auto-installed via requirements; available on Colab)
- 8GB+ RAM (16GB recommended)
- GPU optional but recommended

**Steps:**

1. **Ensure dependencies are installed:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare training data:**
   ```bash
   # Create synthetic data
   python prepare_data.py --sample --prepare
   
   # OR download real data
   python prepare_data.py --download --prepare
   ```

3. **Train the model:**
   ```bash
   # Basic training
   python train_model.py
   
   # With custom parameters
   python train_model.py \
     --epochs 100 \
     --batch-size 32 \
     --data-dir data/raw \
     --output-dir models
   ```

4. **Monitor progress:**
   - Check `logs/training_log.csv` for metrics
   - View TensorBoard: `tensorboard --logdir logs/tensorboard`
   - Training plot saved to `models/training_history.png`

**Local Training Parameters:**
```bash
--epochs 100           # Number of training epochs
--batch-size 32        # Batch size (adjust for memory)
--data-dir data/raw    # Training data directory
--output-dir models    # Output directory for model
```

### Option 3: Cloud GPU Services ☁️

**Amazon SageMaker:**
```python
# Use the train_model.py script
# Configure SageMaker notebook with GPU instance
# Upload data to S3
```

**Azure ML:**
```python
# Use Azure ML compute
# Configure GPU cluster
# Run train_model.py as experiment
```

**Paperspace Gradient:**
- Upload project to Gradient
- Run as notebook or job
- Use GPU instances

## 📊 Training Data

### Synthetic Data (Quick Start)

For testing and development:
```bash
python prepare_data.py --sample
```

Creates 1,000 synthetic tsunami events with:
- Random earthquake parameters
- Simulated ocean conditions
- Balanced classes (95% no tsunami, 5% tsunami)

### Real Data (Production)

For production deployment:

1. **NOAA Global Tsunami Database:**
   ```bash
   python prepare_data.py --download
   ```
   Downloads historical tsunami events from NOAA

2. **GEBCO Bathymetry:**
   - Visit [GEBCO](https://www.gebco.net/data_and_products/gridded_bathymetry_data/)
   - Download Indian Ocean region (40°E to 110°E, 20°S to 30°N)
   - Save to `data/raw/GEBCO_*.nc`

3. **Historical Earthquake Data:**
   - Automatically fetched from USGS during training
   - No manual download needed

## ⚙️ Training Configuration

Edit `config/config.yaml` to customize:

### Model Architecture
```yaml
model:
  architecture:
    cnn_filters: [64, 128, 256]
    cnn_kernel_size: [3, 3, 3]
    lstm_units: [128, 64]
    dense_units: [64, 32]
    dropout_rate: 0.3
```

### Training Parameters
```yaml
model:
  training:
    batch_size: 32
    epochs: 100
    validation_split: 0.2
    learning_rate: 0.001
    early_stopping_patience: 15
    reduce_lr_patience: 7
```

### Input Features
```yaml
model:
  input_features:
    earthquake:
      - magnitude
      - depth
      - latitude
      - longitude
    ocean:
      - sea_level_anomaly
      - wave_height
      - wave_period
    spatial:
      - bathymetry
      - distance_to_coast
    temporal_window: 72  # hours
```

## 📈 Monitoring Training

### TensorBoard
```bash
# Start TensorBoard
tensorboard --logdir logs/tensorboard

# Open browser to http://localhost:6006
```

View:
- Loss curves (training and validation)
- Accuracy metrics
- AUC scores
- Model graphs
- Histograms

### CSV Logs
```bash
# View training log
cat logs/training_log.csv

# Plot with pandas
python -c "
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('logs/training_log.csv')
df[['loss', 'val_loss']].plot()
plt.show()
"
```

### Command-Line Output
Training displays:
- Epoch progress bars
- Loss values per epoch
- Validation metrics
- Best model checkpoints
- Estimated time remaining

## 🎓 Training Tips

### For Best Results:

1. **Use GPU acceleration:**
   - Google Colab: Free T4 GPU
   - Local: NVIDIA GPU with CUDA
   - Cloud: AWS/Azure GPU instances

2. **Monitor for overfitting:**
   - Watch validation loss
   - Early stopping enabled by default
   - Reduce model complexity if needed

3. **Adjust batch size:**
   - GPU: 64-128
   - CPU: 16-32
   - Memory limited: 8-16

4. **Learning rate scheduling:**
   - Automatic reduction on plateau
   - Start with 0.001
   - Can try 0.0001 for fine-tuning

5. **Data augmentation:**
   - Use more training data
   - Balance classes
   - Normalize features

### Common Issues:

**Out of Memory:**
```python
# Reduce batch size
batch_size = 16

# Or use gradient accumulation
# Set in config or code
```

**Not Converging:**
```python
# Increase learning rate
learning_rate = 0.01

# Or increase epochs
epochs = 200
```

**Overfitting:**
```python
# Increase dropout
dropout_rate = 0.5

# Or add regularization
# L2 regularization in model code
```

## 💾 Saving and Loading Models

### During Training
Models are automatically saved:
- `models/checkpoints/best_model.keras` - Best validation loss
- `models/scalers/` - Data scalers (needed for inference)

### After Training
```python
from src.models import TsunamiPredictionModel

# Load trained model
model = TsunamiPredictionModel(config)
model.load_model('models/best_model.keras')

# Load scalers
preprocessor.load_scalers('models/scalers')
```

## 🔄 Transfer Learning

Fine-tune existing model:

```python
# Load pre-trained model
model.load_model('models/best_model.keras')

# Freeze early layers
for layer in model.model.layers[:-10]:
    layer.trainable = False

# Train with lower learning rate
model.compile_model(learning_rate=0.0001)
trainer.train(X_train, y_train, X_val, y_val)
```

## 📊 Expected Performance

After proper training:

**Metrics:**
- Validation Accuracy: > 90%
- AUC Score: > 0.85
- Precision: > 0.80
- Recall: > 0.75

**Inference:**
- Prediction Time: < 2 seconds
- Throughput: 100+ predictions/sec
- Memory Usage: ~1GB

## 🚀 Next Steps After Training

1. **Test the model:**
   ```bash
   python monitor.py --once
   ```

2. **Deploy the application:**
   ```bash
   python main.py
   ```

3. **Monitor in production:**
   ```bash
   python monitor.py --interval 300
   ```

4. **Evaluate performance:**
   - Check alert accuracy
   - Monitor false positives/negatives
   - Retrain if needed

---

**Need Help?**
- Check [README.md](README.md) for full documentation
- See [API_EXAMPLES.md](API_EXAMPLES.md) for usage examples
- Open an issue on GitHub for support
