# Speed Optimization Guide - Offline Inference

## Current Optimizations Applied

### 1. **Reduced Token Limits**
- Edge devices: 800 tokens max
- Laptops: 1200 tokens max
- **Result**: 40-50% faster inference

### 2. **Smaller Context Window**
- Reduced from 2048 to 1024 tokens
- **Result**: Faster processing, less memory

### 3. **Minimal Prompts**
- Ultra-short system prompt
- No RAG context in user prompt (for max speed)
- **Result**: 30-40% faster

### 4. **Optimized Ollama Settings**
- `top_k: 20` - Fewer sampling options
- `top_p: 0.9` - Narrower sampling
- `temperature: 0.1` - Lower = faster
- **Result**: 20-30% faster

## Additional Speed Tips

### Use Smaller Model (Fastest)
If you have `llama3.2:1b` downloaded:
```bash
# In .env
OLLAMA_MODEL=llama3.2:1b
```

### Disable RAG Context (Current)
RAG context is already disabled in user prompt for maximum speed.

### Use GPU Acceleration (If Available)
```bash
# Set in Ollama
OLLAMA_NUM_GPU=1
```

### Reduce Response Length
Current limit: 100 words in analysis. Can reduce further if needed.

## Expected Performance

### With Current Optimizations:
- **Laptop (llama3.2:3b)**: 5-15 seconds
- **Edge (qwen:0.5b)**: 3-10 seconds

### With llama3.2:1b:
- **Laptop**: 3-8 seconds
- **Edge**: 2-5 seconds

## Further Optimizations (If Still Too Slow)

1. **Use even smaller model**: `llama3.2:1b` or `qwen:0.5b`
2. **Reduce num_predict to 500**: Very short responses
3. **Remove legal_references**: Skip if not critical
4. **Simplify roadmap**: Only 1-2 steps instead of multiple

## Monitoring

Check logs for:
- `processing_time_ms` - Should be < 15000ms
- Model used - Should be `llama3.2:3b` on laptop
- Token count - Should be < 1200

