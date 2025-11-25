#!/bin/bash
# Complete offline setup script for Jetson Nano
# This script sets up everything needed for offline operation

set -e  # Exit on error

echo "🚀 VU Legal AID - Complete Offline Setup for Jetson Nano"
echo "========================================================="
echo ""

# Step 1: Check if running on Jetson
if [ -f "/proc/device-tree/model" ]; then
    MODEL=$(cat /proc/device-tree/model)
    echo "📱 Detected device: $MODEL"
else
    echo "⚠️  Not detected as Jetson, but continuing setup..."
fi

# Step 2: Install Ollama
echo ""
echo "📦 Step 1: Installing Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama already installed"
else
    echo "📥 Downloading Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "✅ Ollama installed"
fi

# Step 3: Download Ollama models
echo ""
echo "📦 Step 2: Downloading Ollama models..."
echo "   This may take 20-40 minutes..."

# Start Ollama service
ollama serve &
OLLAMA_PID=$!
sleep 5  # Wait for Ollama to start

# Download recommended model (fastest for Jetson Nano)
echo "📥 Downloading qwen:0.5b (RECOMMENDED - fastest, ~300MB)..."
ollama pull qwen:0.5b || echo "⚠️  Failed to download qwen:0.5b"

# Optional alternative models
echo ""
read -p "Download alternative models? (llama3.2:1b, llama3.2:3b) [N]: " download_alt
if [[ $download_alt =~ ^[Yy]$ ]]; then
    echo "📥 Downloading llama3.2:1b (alternative)..."
    ollama pull llama3.2:1b || echo "⚠️  Failed to download llama3.2:1b"
    
    echo "📥 Downloading llama3.2:3b (alternative, better quality)..."
    ollama pull llama3.2:3b || echo "⚠️  Failed to download llama3.2:3b"
fi

# Stop Ollama (will be started by systemd later)
kill $OLLAMA_PID 2>/dev/null || true

# Step 4: Install Python dependencies
echo ""
echo "📦 Step 3: Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install openai-whisper pyttsx3

# Step 5: Download Whisper models
echo ""
echo "📦 Step 4: Downloading Whisper models..."
echo "   This may take 10-20 minutes..."
python3 << EOF
import whisper
from app.core.edge_optimization import get_optimal_whisper_model

model_size = get_optimal_whisper_model()
print(f"📥 Downloading {model_size} model...")
try:
    whisper.load_model(model_size)
    print(f"✅ {model_size} downloaded")
except Exception as e:
    print(f"⚠️  Error: {e}")
    print("📥 Trying tiny model as fallback...")
    try:
        whisper.load_model("tiny")
        print("✅ tiny model downloaded")
    except Exception as e2:
        print(f"❌ Fallback failed: {e2}")
EOF

# Step 6: Install system TTS
echo ""
echo "📦 Step 5: Installing system TTS..."
sudo apt-get update
sudo apt-get install -y espeak espeak-data || echo "⚠️  Failed to install espeak"

# Step 7: Create systemd service for Ollama
echo ""
echo "📦 Step 6: Setting up Ollama service..."
sudo tee /etc/systemd/system/ollama.service > /dev/null << EOF
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Summary:"
echo "   ✅ Ollama installed and models downloaded"
echo "   ✅ Whisper models downloaded"
echo "   ✅ Offline TTS configured"
echo "   ✅ Ollama service enabled"
echo ""
echo "🚀 Next steps:"
echo "   1. Set OLLAMA_MODEL=qwen:0.5b in backend/.env (already default)"
echo "   2. Start backend: uvicorn app.main:app --reload"
echo "   3. Test: python scripts/test_ollama.py"
echo ""
echo "💡 qwen:0.5b is optimized for Jetson Nano:"
echo "   - Fastest inference speed"
echo "   - Lowest memory usage (~300MB)"
echo "   - Supports multiple languages (English, Hindi, etc.)"
echo ""
echo "💡 Your system is now ready for offline operation!"

