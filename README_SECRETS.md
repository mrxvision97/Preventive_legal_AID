# API Keys and Secrets Configuration

## Quick Setup

Your API keys are now configured with defaults. The system supports:

1. **Cloud Storage** (AWS Secrets Manager) - Recommended for production
2. **Environment Variables** - For local development
3. **Config Defaults** - Fallback values

## Current Configuration

### Redis (Redis Labs Cloud)
- **Host**: `redis-11431.c305.ap-south-1-1.ec2.cloud.redislabs.com`
- **Port**: `11431`
- **Username**: `default`
- **Password**: ✅ Configured (stored in config)

### LangCache
- **API Key**: ✅ Configured (stored in config)

### OpenAI
- Set your `OPENAI_API_KEY` in `.env` file or AWS Secrets Manager

### Pinecone
- Set your `PINECONE_API_KEY` in `.env` file or AWS Secrets Manager

## Setting Up Secrets

### Option 1: Environment Variables (.env file)

Create `backend/.env`:

```bash
OPENAI_API_KEY=your-openai-key
PINECONE_API_KEY=your-pinecone-key
```

### Option 2: AWS Secrets Manager (Production)

Run the setup script:
```bash
cd backend
python scripts/setup_secrets.py
```

This will store all keys securely in AWS Secrets Manager.

## Offline/Online Mode

The system automatically:
- ✅ Uses **OpenAI GPT-4o** when online
- ✅ Falls back to **Ollama** when offline
- ✅ Detects connectivity automatically

### To Use Offline Mode:

1. Install Ollama: https://ollama.ai/download
2. Download a model:
   ```bash
   ollama pull llama3.2
   ```
3. Start Ollama:
   ```bash
   ollama serve
   ```

The system will automatically use Ollama if OpenAI is unavailable.

## Testing

### Test Redis Connection:
```bash
cd backend
python scripts/test_redis.py
```

### Test Ollama:
```bash
cd backend
python scripts/test_ollama.py
```

## Security Notes

- ✅ Redis password is stored in config (can be overridden)
- ✅ LangCache key is stored in config (can be overridden)
- ⚠️ For production, use AWS Secrets Manager
- ⚠️ Never commit `.env` files to Git
- ✅ `.gitignore` already excludes `.env` files

