# Testing Offline Mode on Laptop

This guide helps you test VU Legal AID in offline mode using Ollama on your laptop.

## Prerequisites

✅ **Ollama installed and running**
```bash
# Check if Ollama is running
ollama list

# If not running, start it:
ollama serve
```

✅ **Model downloaded: llama3.2:3b**
```bash
# Verify model is downloaded
ollama list

# Should show: llama3.2:3b
```

## Quick Setup for Offline Testing

### Step 1: Configure for Offline Mode

Create or update `backend/.env`:

```bash
# Force offline mode
USE_OFFLINE_MODE=true

# Use your downloaded model
OLLAMA_MODEL=llama3.2:3b

# Ollama URL (default)
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Leave OpenAI key empty to ensure offline
OPENAI_API_KEY=
```

### Step 2: Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

You should see in the logs:
```
Laptop/Desktop detected - using full-featured models (OpenAI preferred)
```

But since `USE_OFFLINE_MODE=true`, it will use Ollama instead.

### Step 3: Test the API

#### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

#### Test 2: Device Detection
```bash
python backend/scripts/test_device_detection.py
```

Expected output:
- Device Type: Laptop/Desktop
- Recommended Ollama Model: llama3.2:3b
- Ollama: ✅ Available

#### Test 3: Query Analysis (via API)

```bash
curl -X POST "http://localhost:8000/api/v1/public/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are my rights if my landlord increases rent suddenly?",
    "domain": "civil",
    "language": "en"
  }'
```

## Testing with Python Script

Create a test script:

```python
# test_offline.py
import asyncio
from app.services.model_service import analyze_legal_query_with_fallback

async def test():
    result = await analyze_legal_query_with_fallback(
        query_text="What are my rights if my landlord increases rent suddenly?",
        domain="civil",
        user_context={"user_type": "citizen"},
        language="en",
        rag_context=None,
        prefer_online=False  # Force offline
    )
    print(result)

asyncio.run(test())
```

Run it:
```bash
python test_offline.py
```

## Expected Behavior

### With `USE_OFFLINE_MODE=true`:

1. **Device Detection**: Laptop (not edge device)
2. **Model Selection**: llama3.2:3b (your downloaded model)
3. **Service Used**: Ollama (offline)
4. **Response Time**: 5-15 seconds (depending on your laptop)
5. **Quality**: Good (llama3.2:3b is a quality model)

### Logs to Watch For:

```
INFO: Using Ollama (OpenAI not available or prefer_online=False)
INFO: Using Ollama local model for analysis.
INFO: Loading Whisper model model_size=base
```

## Troubleshooting

### Issue: "Ollama connection failed"

**Solution:**
```bash
# Check if Ollama is running
ollama list

# If not, start it:
ollama serve

# Or on Windows:
# Start Ollama from Start Menu or run: ollama serve
```

### Issue: "Model not found"

**Solution:**
```bash
# List available models
ollama list

# If llama3.2:3b is not listed, download it:
ollama pull llama3.2:3b
```

### Issue: "Still using OpenAI"

**Check:**
1. Is `USE_OFFLINE_MODE=true` in `.env`?
2. Is `OPENAI_API_KEY` empty or commented out?
3. Restart the server after changing `.env`

### Issue: "Slow responses"

**This is normal for offline mode:**
- llama3.2:3b takes 5-15 seconds per query
- First query may be slower (model loading)
- Subsequent queries are faster (cached)

## Performance Tips

1. **Keep Ollama running**: Don't close the `ollama serve` window
2. **First query is slow**: Model needs to load into memory
3. **Subsequent queries are faster**: Model stays in memory
4. **Close other apps**: Free up RAM for better performance

## Testing Different Models

If you want to test with a different model:

```bash
# Download another model
ollama pull qwen:0.5b

# Update .env
OLLAMA_MODEL=qwen:0.5b

# Restart server
```

## Next Steps

Once offline testing works:

1. ✅ Test query processing
2. ✅ Test voice transcription (if Whisper installed)
3. ✅ Test TTS (if pyttsx3 installed)
4. ✅ Test document upload
5. ✅ Deploy to Jetson Nano

## Verification Checklist

- [ ] Ollama is running (`ollama list` works)
- [ ] Model downloaded (`llama3.2:3b` in list)
- [ ] `.env` configured (`USE_OFFLINE_MODE=true`)
- [ ] Backend starts without errors
- [ ] Test query returns response
- [ ] Response time is reasonable (5-15 seconds)

## Quick Test Command

Run this to test everything at once:

```bash
# 1. Check Ollama
ollama list

# 2. Test device detection
python backend/scripts/test_device_detection.py

# 3. Test query (replace with your actual query)
curl -X POST "http://localhost:8000/api/v1/public/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Indian Contract Act?", "domain": "civil", "language": "en"}'
```

If all three work, your offline setup is ready! 🎉

