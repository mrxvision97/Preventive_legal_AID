# Device Detection & Model Selection

VU Legal AID automatically detects the device type and selects optimal models.

## Device Types

### 🖥️ Laptops/Desktops (Development)
- **Detection**: Not a Jetson Nano or ARM edge device
- **Model Priority**: 
  1. OpenAI GPT-4o (if available) - Best quality
  2. Ollama llama3.2:3b (fallback) - Good quality
- **Optimizations**: Full context, better prompts, no memory limits

### 🔧 Jetson Nano (Edge Device)
- **Detection**: Detects Jetson via `/proc/device-tree/model`
- **Model Priority**:
  1. Ollama qwen:0.5b (default) - Fastest, lowest memory
  2. OpenAI (fallback if available)
- **Optimizations**: Reduced context, optimized prompts, memory limits

## Automatic Detection

The system automatically detects your device:

```python
# Edge device detection checks:
1. /proc/device-tree/model contains "jetson" or "nano"
2. ARM architecture (excluding x86 laptops)
3. Environment variable EDGE_DEVICE=true
4. Config setting FORCE_EDGE_MODE=true
```

## Manual Override

### Force Edge Mode on Laptop (for testing)

```bash
# In backend/.env
FORCE_EDGE_MODE=true
# or
EDGE_DEVICE=true
```

### Force Laptop Mode on Jetson (not recommended)

```bash
# In backend/.env
EDGE_DEVICE=false
```

## Model Selection Logic

### On Laptops:
```python
# Default behavior:
1. Try OpenAI GPT-4o (best quality)
2. If unavailable → Use Ollama llama3.2:3b
3. Auto-detects optimal Ollama model based on available models
```

### On Jetson Nano:
```python
# Default behavior:
1. Use Ollama qwen:0.5b (fastest)
2. If unavailable → Try OpenAI (if online)
3. Auto-optimizes for edge device constraints
```

## Testing on Laptop

### Test with OpenAI (default):
```bash
# Just run normally - will use OpenAI if available
uvicorn app.main:app --reload
```

### Test with Ollama (offline mode):
```bash
# Set in backend/.env
USE_OFFLINE_MODE=true
# or
FORCE_EDGE_MODE=true  # Forces edge optimizations too
```

### Test with specific Ollama model:
```bash
# In backend/.env
OLLAMA_MODEL=llama3.2:3b
USE_OFFLINE_MODE=true
```

## Deployment on Jetson Nano

### Automatic (Recommended):
```bash
# Just deploy - system auto-detects Jetson Nano
# Uses qwen:0.5b automatically
```

### Manual Configuration:
```bash
# In backend/.env (optional, already default)
OLLAMA_MODEL=qwen:0.5b
EDGE_DEVICE=true  # Optional, auto-detected
```

## Verification

Check which device type is detected:

```python
from app.core.edge_optimization import is_edge_device, optimize_for_edge

is_edge = is_edge_device()
print(f"Is edge device: {is_edge}")

optimizations = optimize_for_edge()
print(f"Optimizations: {optimizations}")
```

## Performance Comparison

### Laptop (with OpenAI):
- Query processing: 2-5 seconds
- Best quality responses
- Full context windows

### Laptop (with Ollama llama3.2:3b):
- Query processing: 5-15 seconds
- Good quality responses
- Full context windows

### Jetson Nano (with qwen:0.5b):
- Query processing: 3-10 seconds
- Good quality for edge device
- Optimized context windows

## Troubleshooting

### Laptop using edge model:
- Check `EDGE_DEVICE` environment variable
- Check `FORCE_EDGE_MODE` in config
- Verify device detection: `python -c "from app.core.edge_optimization import is_edge_device; print(is_edge_device())"`

### Jetson using laptop model:
- Check `/proc/device-tree/model` exists
- Verify Jetson detection
- Set `EDGE_DEVICE=true` explicitly

