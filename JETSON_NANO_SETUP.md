# Jetson Nano Setup Guide - VU Legal AID

## 🚀 Complete Offline Setup for Edge Devices

This guide helps you set up VU Legal AID to work completely offline on Jetson Nano or similar edge devices.

## Prerequisites

- Jetson Nano with JetPack 4.6+ or 5.0+
- At least 4GB RAM (8GB recommended)
- 32GB+ SD card or SSD
- Internet connection for initial setup

## Step 1: Install Ollama

```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
```

## Step 2: Download Optimized Models

Run the setup script:

```bash
cd backend
python scripts/setup_ollama.py
```

Or manually download the recommended model:

```bash
# RECOMMENDED: Fastest model (~300MB) - BEST for Jetson Nano
ollama pull qwen:0.5b
```

**Recommended for Jetson Nano**: `qwen:0.5b` 
- ✅ Fastest inference speed
- ✅ Lowest memory usage (~300MB)
- ✅ Supports multiple languages (English, Hindi, etc.)
- ✅ Optimized for edge devices

Alternative models (if needed):
```bash
# Alternative: Smaller model (1.3GB)
ollama pull llama3.2:1b

# Alternative: Better quality but slower (2.0GB)
ollama pull llama3.2:3b
```

## Step 3: Install Offline Voice Dependencies

```bash
# Install Whisper for offline transcription
pip install openai-whisper

# Install offline TTS
pip install pyttsx3

# For Jetson Nano, use CPU-optimized PyTorch
# (Already included in requirements.txt)
```

## Step 4: Download Whisper Models

Whisper models are downloaded automatically on first use. For Jetson Nano, recommended models:

- **tiny** (~39MB) - Fastest, lowest quality
- **base** (~74MB) - Good balance (recommended)
- **small** (~244MB) - Better quality, slower

The system auto-selects based on available memory.

## Step 5: Configure for Edge Device

Update `backend/.env`:

```bash
# Use edge-optimized Ollama model (fastest for Jetson Nano)
OLLAMA_MODEL=qwen:0.5b
OLLAMA_BASE_URL=http://localhost:11434

# Force offline mode (optional)
USE_OFFLINE_MODE=true
```

## Step 6: Test Offline Features

### Test Ollama:
```bash
cd backend
python scripts/test_ollama.py
```

### Test Whisper:
```python
from app.services.offline_voice_service import transcribe_audio_offline
result = await transcribe_audio_offline("test_audio.webm", "hi", "base")
print(result["text"])
```

### Test TTS:
```python
from app.services.offline_voice_service import synthesize_speech_offline
audio = await synthesize_speech_offline("Hello, this is a test", "en")
```

## Performance Optimizations

### For Jetson Nano (4GB RAM):
- Use `qwen:0.5b` model (RECOMMENDED - fastest)
- Use `tiny` Whisper model
- Limit RAG chunks to 3
- Reduce max tokens to 2000

### For Jetson Nano (8GB RAM):
- Use `qwen:0.5b` model (RECOMMENDED - fastest)
- Use `base` Whisper model
- Limit RAG chunks to 5
- Max tokens: 3000

## Automatic Optimization

The system automatically detects Jetson Nano and applies optimizations:

- ✅ Smaller model selection
- ✅ Reduced context windows
- ✅ Optimized prompts
- ✅ Caching enabled
- ✅ Lower temperature for consistency

## Offline Mode Features

### ✅ Fully Offline:
- Legal query analysis (Ollama)
- Voice transcription (Whisper)
- Text-to-speech (pyttsx3)
- Document processing
- Multilingual support

### ⚠️ Requires Internet:
- Pinecone vector database (can use local alternative)
- Initial model downloads

## Memory Management

Jetson Nano has limited RAM. The system:

1. **Auto-detects** available memory
2. **Selects optimal models** automatically
3. **Limits context** to prevent OOM
4. **Uses caching** to reduce computation

## Troubleshooting

### Out of Memory Errors:
```bash
# Use fastest model (already default)
export OLLAMA_MODEL=qwen:0.5b

# Use tiny Whisper
# System auto-selects based on memory
```

### Slow Performance:
- Use `qwen:0.5b` (already default - fastest)
- Use `tiny` Whisper model
- Reduce max_tokens in prompts
- Enable GPU acceleration (if available)

### Model Not Found:
```bash
# List downloaded models
ollama list

# Download if missing
ollama pull llama3.2:3b
```

## Production Deployment

For production on Jetson Nano:

1. **Use systemd** to auto-start Ollama:
```bash
sudo systemctl enable ollama
sudo systemctl start ollama
```

2. **Set up swap** if needed:
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

3. **Monitor resources**:
```bash
# Watch memory usage
watch -n 1 free -h

# Watch GPU usage
sudo tegrastats
```

## Expected Performance

### Jetson Nano (4GB):
- Query processing: 10-30 seconds
- Voice transcription: 5-15 seconds
- TTS generation: 1-3 seconds

### Jetson Nano (8GB):
- Query processing: 5-15 seconds
- Voice transcription: 3-10 seconds
- TTS generation: < 1 second

## Next Steps

1. ✅ Models downloaded
2. ✅ Voice services configured
3. ✅ Edge optimizations enabled
4. 🚀 Ready for offline use!

The system will automatically use offline models when internet is unavailable.

