#!/bin/bash
# Install edge device dependencies for Jetson Nano

echo "🚀 Installing Edge Device Dependencies"
echo "====================================="

# Install system dependencies
echo "📦 Installing system packages..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    ffmpeg \
    portaudio19-dev \
    espeak \
    espeak-data

# Install Python dependencies
echo "📦 Installing Python packages..."
pip3 install --upgrade pip

# Install Whisper (offline transcription)
echo "📥 Installing Whisper..."
pip3 install openai-whisper

# Install offline TTS
echo "📥 Installing offline TTS..."
pip3 install pyttsx3

# Install PyTorch for Jetson Nano (CPU version)
echo "📥 Installing PyTorch for Jetson..."
# Note: Use Jetson-specific PyTorch wheel if available
# pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "Next steps:"
echo "1. Run: python3 scripts/setup_ollama.py"
echo "2. Download models: ollama pull llama3.2:3b"
echo "3. Start Ollama: ollama serve"

