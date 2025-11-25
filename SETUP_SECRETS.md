# Setting Up Cloud Secrets and Offline/Online Model Support

## Overview

VU Legal AID supports:
- **Cloud-based secret storage** (AWS Secrets Manager)
- **Online mode**: OpenAI GPT-4o when internet is available
- **Offline mode**: Ollama local models when offline
- **Automatic fallback** between online and offline models

## 1. Setting Up Secrets

### Option A: AWS Secrets Manager (Recommended)

1. Install AWS CLI and configure:
```bash
aws configure
```

2. Run the setup script:
```bash
cd backend
python scripts/setup_secrets.py
```

3. Enter your API keys when prompted:
   - OpenAI API Key
   - Redis Password: `QtdXhZHAhwe11zCjqLOm1UkU8ud9o5qi`
   - LangCache API Key: `wy4ECQMIU-DhqXrfFongfMQbzYOkOOk8mZnvYVY1VvFvfW2MVr3thSzCSr2JFdK20oIBgOvV5BEyOESlCny_6_M2dqKjEGU9I470l0GLIwgsugntnP9DthQK71uInD3eUgNFecMTloBm5DK7r0GupYTHXx67wCXBPPOt_YMkppOOu2G-ziWa3h7iHHyjWDicKKBtwxRZQT8lYv4VDWA2wegLyk409A0SqRfNwp687eNrKWT1`
   - Pinecone API Key

### Option B: Environment Variables

Set these in your `.env` file or system environment:

```bash
# Redis (Redis Labs Cloud)
REDIS_HOST=redis-11431.c305.ap-south-1-1.ec2.cloud.redislabs.com
REDIS_PORT=11431
REDIS_USERNAME=default
REDIS_PASSWORD=QtdXhZHAhwe11zCjqLOm1UkU8ud9o5qi

# LangCache
LANGCACHE_API_KEY=wy4ECQMIU-DhqXrfFongfMQbzYOkOOk8mZnvYVY1VvFvfW2MVr3thSzCSr2JFdK20oIBgOvV5BEyOESlCny_6_M2dqKjEGU9I470l0GLIwgsugntnP9DthQK71uInD3eUgNFecMTloBm5DK7r0GupYTHXx67wCXBPPOt_YMkppOOu2G-ziWa3h7iHHyjWDicKKBtwxRZQT8lYv4VDWA2wegLyk409A0SqRfNwp687eNrKWT1

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Pinecone
PINECONE_API_KEY=your-pinecone-api-key
```

## 2. Setting Up Ollama (Offline Mode)

### Install Ollama

**Windows:**
1. Download from https://ollama.ai/download
2. Install and start Ollama service

**Linux/Mac:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Download Legal Model

```bash
# Recommended models for legal analysis
ollama pull llama3.2        # Best balance
ollama pull mistral         # Alternative
ollama pull qwen2.5         # Good for multilingual
```

### Verify Ollama is Running

```bash
ollama list
# Should show installed models
```

## 3. How It Works

### Automatic Model Selection

The system automatically:
1. **Checks OpenAI connectivity** (5 second timeout)
2. **If online**: Uses GPT-4o for best results
3. **If offline**: Falls back to Ollama local model
4. **If both fail**: Returns error message

### Model Service Flow

```
User Query
    ↓
Check OpenAI Connection
    ↓
    ├─→ Online? → Use GPT-4o
    │
    └─→ Offline? → Use Ollama
        ↓
    Return Analysis
```

## 4. Redis Configuration

The system uses Redis Labs cloud instance:

- **Host**: `redis-11431.c305.ap-south-1-1.ec2.cloud.redislabs.com`
- **Port**: `11431`
- **Username**: `default`
- **Password**: Set in secrets

### LangCache Integration

LangCache provides intelligent caching for AI responses:
- Caches similar queries
- Reduces API costs
- Improves response time
- Works with both OpenAI and Ollama

## 5. Testing

### Test Online Mode
```bash
# Ensure OpenAI API key is set
# Ensure internet connection
# Make a query - should use GPT-4o
```

### Test Offline Mode
```bash
# Disconnect internet or remove OpenAI key
# Ensure Ollama is running: ollama serve
# Make a query - should use Ollama
```

### Test Redis Connection
```python
from app.core.redis import get_redis
redis = await get_redis()
await redis.set('test', 'value')
result = await redis.get('test')
print(result)  # Should print 'value'
```

## 6. Environment Variables Priority

1. **AWS Secrets Manager** (if configured)
2. **Environment Variables** (`.env` file)
3. **Config defaults** (fallback)

## 7. Security Best Practices

- ✅ Never commit `.env` files
- ✅ Use AWS Secrets Manager for production
- ✅ Rotate API keys regularly
- ✅ Use IAM roles for AWS access
- ✅ Enable SSL for Redis connections

## 8. Troubleshooting

### Ollama not found
```bash
# Check if Ollama is running
ollama serve

# Check if model is downloaded
ollama list
```

### Redis connection failed
- Verify Redis Labs credentials
- Check firewall settings
- Ensure SSL is enabled for port 11431

### OpenAI fallback not working
- Check internet connection
- Verify API key is valid
- Check rate limits

## 9. Production Deployment

For production:
1. Store all secrets in AWS Secrets Manager
2. Use IAM roles instead of access keys
3. Enable VPC endpoints for AWS services
4. Use encrypted environment variables
5. Monitor API usage and costs

