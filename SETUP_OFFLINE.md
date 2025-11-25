# Complete Offline Setup Guide

## 🎯 Goal: Fully Offline VU Legal AID on Jetson Nano

This guide sets up VU Legal AID to work completely offline with:
- ✅ Local AI models (Ollama)
- ✅ Offline voice transcription (Whisper)
- ✅ Offline text-to-speech (pyttsx3)
- ✅ Optimized for Jetson Nano performance

## Quick Setup (Automated)

### 1. Run Setup Scripts

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Download Ollama models (automated)
python scripts/auto_download_models.py

# Download Whisper models (automated)
python scripts/download_whisper_models.py
```

### 2. Configure for Offline Mode

Edit `backend/.env`:

```bash
# Force offline mode
USE_OFFLINE_MODE=true

# Use edge-optimized model
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434

# Disable online services (optional)
OPENAI_API_KEY=
```

## Manual Setup

### Step 1: Install Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2: Download Models

```bash
# RECOMMENDED: Fastest model for Jetson Nano (~300MB)
ollama pull qwen:0.5b

# Alternative: Smaller model (faster, less memory)
ollama pull llama3.2:1b

# Alternative: Better quality but slower
ollama pull llama3.2:3b
```

**qwen:0.5b is optimized for Jetson Nano:**
- ✅ Fastest inference speed
- ✅ Lowest memory usage (~300MB)
- ✅ Supports multiple languages

### Step 3: Install Voice Dependencies

```bash
# Install Whisper
pip install openai-whisper

# Install offline TTS
pip install pyttsx3

# For Jetson Nano, install system TTS
sudo apt-get install espeak espeak-data
```

### Step 4: Pre-download Whisper Models

```bash
python backend/scripts/download_whisper_models.py
```

This downloads and caches models for faster first use.

## Optimized Prompts for Edge Devices

The system automatically uses optimized prompts:

### System Prompt (Optimized)
- **Shorter**: Reduced from ~500 to ~200 tokens
- **Direct**: Clear, concise instructions
- **JSON-focused**: Emphasizes structured output

### User Prompt (Optimized)
- **Limited context**: Top 3 RAG chunks (instead of 5)
- **Truncated chunks**: 200 chars per chunk (instead of full)
- **Concise**: "Analyze. Return ONLY JSON"

## Performance Tuning

### For Jetson Nano (4GB RAM):

```bash
# Use fastest model (recommended)
OLLAMA_MODEL=qwen:0.5b
WHISPER_MODEL=tiny

# Reduce context
RAG_CHUNKS=3
MAX_TOKENS=2000
```

### For Jetson Nano (8GB RAM):

```bash
# Use fastest model (recommended)
OLLAMA_MODEL=qwen:0.5b
WHISPER_MODEL=base

# Standard context
RAG_CHUNKS=5
MAX_TOKENS=3000
```

## Testing Offline Features

### Test Ollama:
```bash
ollama run llama3.2:3b "What is Indian Contract Act?"
```

### Test Whisper:
```python
import whisper
model = whisper.load_model("base")
result = model.transcribe("audio.webm", language="hi")
print(result["text"])
```

### Test TTS:
```python
import pyttsx3
engine = pyttsx3.init()
engine.say("Hello, this is a test")
engine.runAndWait()
```

## Voice Features Offline

### Transcription Flow:
1. User records audio (browser)
2. Audio sent to backend
3. System checks: Online? → OpenAI Whisper
4. If offline → Local Whisper
5. Returns transcription

### TTS Flow:
1. User requests audio playback
2. System checks: Online? → OpenAI TTS
3. If offline → pyttsx3
4. Returns WAV audio

## Automatic Optimizations

The system automatically:

1. **Detects Jetson Nano** via `/proc/device-tree/model`
2. **Checks available memory** and selects optimal models
3. **Limits context** to prevent OOM errors
4. **Uses caching** to reduce computation
5. **Optimizes prompts** for faster processing

## Expected Performance (Jetson Nano)

### Query Processing:
- **qwen:0.5b**: 3-10 seconds (FASTEST - recommended)
- **llama3.2:1b**: 5-15 seconds
- **llama3.2:3b**: 10-30 seconds

### Voice Transcription:
- **tiny model**: 3-8 seconds
- **base model**: 5-15 seconds

### Text-to-Speech:
- **pyttsx3**: < 1 second

## Troubleshooting

### Out of Memory:
```bash
# Use smaller models
export OLLAMA_MODEL=llama3.2:1b
export WHISPER_MODEL=tiny

# Add swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Slow Performance:
- Use `llama3.2:1b` instead of `llama3.2:3b`
- Use `tiny` Whisper model
- Reduce `MAX_TOKENS` in prompts
- Enable GPU acceleration (if available)

### Models Not Found:
```bash
# List Ollama models
ollama list

# List Whisper models (check cache)
ls ~/.cache/whisper/
```

## Production Deployment

### Systemd Service for Ollama:

```bash
# Create service file
sudo nano /etc/systemd/system/ollama.service
```

```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=your-user
ExecStart=/usr/local/bin/ollama serve
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable ollama
sudo systemctl start ollama
```

## Verification

Check all services:

```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check Whisper
python -c "import whisper; print('Whisper OK')"

# Check TTS
python -c "import pyttsx3; print('TTS OK')"
```

## ✅ Complete Offline Setup

Once configured:
- ✅ No internet required for queries
- ✅ No internet required for voice
- ✅ Optimized for Jetson Nano
- ✅ Automatic model selection
- ✅ Best performance possible

Your VU Legal AID is now fully offline-capable! 🎉

