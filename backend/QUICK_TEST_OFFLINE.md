# Quick Start: Test Offline Mode on Laptop

## ✅ Prerequisites Check

1. **Ollama installed and running:**
```bash
ollama list
# Should show your models
```

2. **Model downloaded:**
```bash
ollama list
# Should show: llama3.2:3b
```

## 🚀 Quick Setup (3 Steps)

### Step 1: Configure `.env`

Create `backend/.env` file:

```bash
# Offline Mode Configuration
USE_OFFLINE_MODE=true
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434

# Leave OpenAI empty for offline
OPENAI_API_KEY=
```

### Step 2: Start Ollama (if not running)

```bash
# In a separate terminal
ollama serve
```

### Step 3: Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

## 🧪 Quick Test

Run the test script:

```bash
python backend/scripts/test_offline_quick.py
```

This will:
- ✅ Check Ollama connection
- ✅ Verify model availability
- ✅ Test a sample query
- ✅ Show results

## 📝 Manual API Test

```bash
curl -X POST "http://localhost:8000/api/v1/public/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are my rights if my landlord increases rent?",
    "domain": "civil",
    "language": "en"
  }'
```

## ⚡ Expected Results

- **Response Time**: 5-15 seconds (first query may be slower)
- **Model Used**: llama3.2:3b
- **Quality**: Good (llama3.2:3b is a quality model)

## 🔧 Troubleshooting

### Ollama not running?
```bash
ollama serve
```

### Model not found?
```bash
ollama pull llama3.2:3b
```

### Still using OpenAI?
- Check `.env`: `USE_OFFLINE_MODE=true`
- Restart backend server

## ✅ Success Indicators

- ✅ Backend starts without errors
- ✅ Test script completes successfully
- ✅ API returns legal analysis
- ✅ Response time is reasonable (5-15 seconds)

If all check, you're ready! 🎉

