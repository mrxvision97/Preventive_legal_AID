#!/bin/bash
# Setup script for Jetson Nano - Optimized for edge devices

echo "🚀 Setting up VU Legal AID for Jetson Nano"
echo "=========================================="

# Install Ollama
if ! command -v ollama &> /dev/null; then
    echo "📥 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama already installed"
fi

# Download optimized models for Jetson Nano
echo ""
echo "📦 Downloading optimized models for Jetson Nano..."
echo "   (This may take 5-15 minutes depending on internet speed)"

# Download recommended model (fastest, lowest parameters)
echo "📥 Downloading qwen:0.5b (RECOMMENDED - fastest, ~300MB)..."
ollama pull qwen:0.5b
echo "✅ Downloaded qwen:0.5b (~300MB) - FASTEST for Jetson Nano"

# Optional: Download alternative models
echo ""
read -p "Download alternative models? (llama3.2:1b, llama3.2:3b) [N]: " download_alt
if [[ $download_alt =~ ^[Yy]$ ]]; then
    ollama pull llama3.2:1b
    echo "✅ Downloaded llama3.2:1b (1.3GB)"
    
    ollama pull llama3.2:3b
    echo "✅ Downloaded llama3.2:3b (2.0GB)"
fi

echo ""
echo "✅ Model setup complete!"
echo ""
echo "💡 RECOMMENDED model for Jetson Nano: qwen:0.5b"
echo "   - Fastest inference"
echo "   - Lowest memory usage (~300MB)"
echo "   - Supports multiple languages"
echo "   Set in .env: OLLAMA_MODEL=qwen:0.5b"

