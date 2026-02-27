#!/bin/bash

# Quick Start Script for Tsunami Early Warning System

echo "================================================"
echo "🌊 Tsunami Early Warning System - Quick Start"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Prepare data
echo "Preparing sample data..."
python3 prepare_data.py --sample --prepare
echo "✓ Data prepared"
echo ""

# Train model (quick training with few epochs)
echo "Training model (this may take several minutes)..."
python3 train_model.py --epochs 10 --batch-size 32
echo "✓ Model trained"
echo ""

# Start web server
echo "================================================"
echo "✅ Setup complete!"
echo "================================================"
echo ""
echo "To start the web server, run:"
echo "  python3 main.py"
echo ""
echo "To run real-time monitoring, run:"
echo "  python3 monitor.py"
echo ""
echo "To access the dashboard:"
echo "  http://localhost:5000"
echo ""
echo "================================================"
