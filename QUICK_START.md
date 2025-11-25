# Quick Start Guide - VU Legal AID

## 🚀 Setup in 5 Minutes

### 1. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure API Keys

Create `backend/.env` file:

```bash
# OpenAI (Required for online mode)
OPENAI_API_KEY=your-openai-api-key

# Pinecone (Required for RAG)
PINECONE_API_KEY=your-pinecone-api-key

# Redis and LangCache are already configured with defaults
# But you can override them if needed:
# REDIS_PASSWORD=your-redis-password
# LANGCACHE_API_KEY=your-langcache-key
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb legal_db

# Install pgvector extension
psql -U postgres -d legal_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run migrations
alembic upgrade head
```

### 4. Start Backend

```bash
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

## 🔄 Offline/Online Mode

### Online Mode (Default)
- Uses OpenAI GPT-4o
- Requires internet connection
- Best quality responses

### Offline Mode (Ollama)
1. Install Ollama: https://ollama.ai/download
2. Download model:
   ```bash
   ollama pull llama3.2
   ```
3. Start Ollama:
   ```bash
   ollama serve
   ```

The system automatically falls back to Ollama if OpenAI is unavailable!

## ✅ Pre-configured

- ✅ Redis: Redis Labs cloud instance
- ✅ LangCache: API key configured
- ✅ Automatic fallback: OpenAI → Ollama
- ✅ Cloud secrets: AWS Secrets Manager support

## 📝 Next Steps

1. Add your OpenAI API key to `.env`
2. Add your Pinecone API key to `.env`
3. Start the services
4. Visit `http://localhost:5173` and start using VU Legal AID!

## 🧪 Test Connections

```bash
# Test Redis
python backend/scripts/test_redis.py

# Test Ollama
python backend/scripts/test_ollama.py
```

