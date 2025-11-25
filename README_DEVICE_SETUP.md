# Device Setup Guide - Laptop & Jetson Nano

VU Legal AID works seamlessly on both laptops (for development) and Jetson Nano (for deployment).

## 🖥️ Development on Laptop

### Quick Start

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure (optional):**
```bash
# backend/.env
OPENAI_API_KEY=your-key-here  # For best quality
# or leave empty to use Ollama
```

3. **Run:**
```bash
uvicorn app.main:app --reload
```

### Model Selection on Laptop

**Default behavior:**
- ✅ **OpenAI GPT-4o** (if API key provided) - Best quality
- ✅ **Ollama llama3.2:3b** (fallback) - Good quality

**To test offline mode:**
```bash
# In backend/.env
USE_OFFLINE_MODE=true
OLLAMA_MODEL=llama3.2:3b  # or qwen:0.5b for testing
```

**To test edge device mode:**
```bash
# In backend/.env
FORCE_EDGE_MODE=true  # Simulates Jetson Nano behavior
```

### Test Device Detection

```bash
python backend/scripts/test_device_detection.py
```

This will show:
- Device type detected
- Recommended models
- Available services
- Which model will be used

## 🔧 Deployment on Jetson Nano

### Quick Start

1. **Run complete setup:**
```bash
bash backend/scripts/complete_offline_setup.sh
```

2. **Or manual setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download model
ollama pull qwen:0.5b

# Install dependencies
pip install -r requirements.txt
```

3. **Run:**
```bash
uvicorn app.main:app --host 0.0.0.0
```

### Automatic Detection

The system **automatically detects Jetson Nano** and:
- ✅ Uses `qwen:0.5b` (fastest model)
- ✅ Applies edge optimizations
- ✅ Limits context to prevent OOM
- ✅ Uses optimized prompts

No configuration needed!

## 🔄 Same Code, Different Behavior

The **same codebase** works on both devices with automatic optimizations:

| Feature | Laptop | Jetson Nano |
|---------|--------|-------------|
| **AI Model** | OpenAI GPT-4o (preferred) | Ollama qwen:0.5b |
| **Fallback** | Ollama llama3.2:3b | OpenAI (if online) |
| **Context** | Full (5 chunks) | Limited (3 chunks) |
| **Prompts** | Full quality | Optimized for speed |
| **Memory** | No limits | Optimized limits |
| **Voice** | Online/Offline | Offline preferred |

## 🧪 Testing Workflow

### 1. Develop on Laptop

```bash
# Use OpenAI for best quality during development
OPENAI_API_KEY=your-key
uvicorn app.main:app --reload
```

### 2. Test Offline Mode on Laptop

```bash
# Test with Ollama (simulate Jetson Nano)
USE_OFFLINE_MODE=true
OLLAMA_MODEL=qwen:0.5b
FORCE_EDGE_MODE=true  # Apply edge optimizations
uvicorn app.main:app --reload
```

### 3. Deploy on Jetson Nano

```bash
# Just deploy - auto-detects and optimizes
uvicorn app.main:app --host 0.0.0.0
```

## 📋 Configuration Reference

### Laptop Configuration

```bash
# backend/.env (for development)
OPENAI_API_KEY=your-key-here  # Optional, for best quality
OLLAMA_MODEL=llama3.2:3b      # Fallback model
USE_OFFLINE_MODE=false        # Use OpenAI when available
```

### Jetson Nano Configuration

```bash
# backend/.env (auto-configured)
OLLAMA_MODEL=qwen:0.5b        # Fastest for edge
USE_OFFLINE_MODE=true         # Prefer offline
# EDGE_DEVICE auto-detected, no need to set
```

### Manual Override

```bash
# Force edge mode on laptop (for testing)
FORCE_EDGE_MODE=true

# Force laptop mode on Jetson (not recommended)
EDGE_DEVICE=false
```

## 🚀 Performance Expectations

### Laptop (with OpenAI):
- Query: 2-5 seconds
- Quality: Best
- Context: Full

### Laptop (with Ollama llama3.2:3b):
- Query: 5-15 seconds
- Quality: Good
- Context: Full

### Jetson Nano (with qwen:0.5b):
- Query: 3-10 seconds
- Quality: Good (optimized for edge)
- Context: Limited (optimized)

## ✅ Verification

### Check Device Detection:
```bash
python backend/scripts/test_device_detection.py
```

### Check Model Availability:
```bash
# Test OpenAI
python backend/scripts/test_openai.py

# Test Ollama
python backend/scripts/test_ollama.py
```

## 🎯 Best Practices

1. **Develop on laptop** with OpenAI for best quality
2. **Test offline mode** on laptop before deploying
3. **Deploy on Jetson Nano** - auto-detects and optimizes
4. **No code changes needed** - same codebase works everywhere

## 📚 Additional Resources

- `DEVICE_DETECTION.md` - Detailed device detection logic
- `JETSON_NANO_SETUP.md` - Jetson Nano specific setup
- `SETUP_OFFLINE.md` - Offline mode setup
- `QUICK_START.md` - Quick start guide

