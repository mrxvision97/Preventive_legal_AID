# VU Legal AID

A comprehensive web-based platform providing AI-powered legal guidance to rural citizens, farmers, and university students in India.

## Project Structure

```
Preventive_legal/
├── backend/          # FastAPI backend application
├── frontend/         # React + TypeScript frontend application
├── docs/            # Documentation
└── README.md        # This file
```

## Technology Stack

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL 15+ with SQLAlchemy 2.0 async ORM
- Redis for caching
- OpenAI GPT-4o for AI analysis
- LangChain for RAG pipeline
- Pinecone/Weaviate for vector database
- Alembic for migrations

### Frontend
- React 18 with TypeScript
- Create React App (CRA) - compatible with Node.js 16+ for Jetson Nano
- Tailwind CSS for styling
- Zustand for state management
- React Hook Form + Zod
- Axios for HTTP requests

## Getting Started

### Prerequisites
- Python 3.11+ (or 3.8+ for Jetson Nano)
- Node.js 16+ (for Jetson Nano Ubuntu 18.04) or Node.js 18+ (for modern systems)
- PostgreSQL 15+ (optional - currently disabled)
- Redis 7+ (optional - for caching)

### Platform-Specific Setup

#### For Laptops/Desktops (Development)

**Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
# Note: Database initialization is currently commented out
uvicorn app.main:app --reload
```

**Frontend Setup:**
```bash
cd frontend
npm install
# Create .env file with REACT_APP_API_URL=http://localhost:8000
npm start  # Starts on port 3000 (CRA default)
```

**For Jetson Nano (Ubuntu 18.04 + Node.js 16):**
```bash
cd frontend
bash setup_jetson_nano.sh  # Automated setup script
# Or manually:
npm install
npm start
```

#### For Jetson Nano 4GB (Edge Device)

**Two Setup Options:**

1. **Offline Mode** (Ollama - No Internet Required):
   - Guide: [`JETSON_NANO_4GB_SETUP.md`](JETSON_NANO_4GB_SETUP.md)
   - Script: `bash backend/scripts/setup_jetson_nano_4gb.sh`
   - Uses: Local Ollama with `qwen:0.5b` model

2. **Cloud Mode** (OpenAI - Internet Required):
   - Guide: [`JETSON_NANO_CLOUD_SETUP.md`](JETSON_NANO_CLOUD_SETUP.md)
   - Script: `bash backend/scripts/setup_jetson_nano_cloud.sh`
   - Uses: OpenAI API (no Ollama needed)

**Key Configuration for Jetson Nano:**
- Use `qwen:0.5b` model (fastest, lowest memory)
- Enable offline mode: `USE_OFFLINE_MODE=true`
- Force edge mode: `FORCE_EDGE_MODE=true`
- Configure 4GB+ swap space (critical!)

## Features

- **AI-powered legal analysis** with risk assessment (OpenAI or Ollama offline)
- **Public chatbot** accessible without login/signup
- **Multilingual support** (Hindi, English, Tamil, Telugu, Bengali, Marathi)
- **Voice input/output** using Whisper (offline) and TTS (pyttsx3)
- **Document upload** and text extraction (PDF, TXT)
- **RAG-based knowledge retrieval** (Pinecone vector database)
- **Offline mode** optimized for edge devices (Jetson Nano)
- **Edge device optimization** with automatic model selection
- User authentication and profiles
- Admin dashboard
- Legal aid center directory

## Platform Support

- ✅ **Laptops/Desktops**: Full features with OpenAI or Ollama
- ✅ **Jetson Nano 4GB**: Optimized offline mode with `qwen:0.5b`
- ✅ **Edge Devices**: Automatic optimization and model selection

## Documentation

- **Jetson Nano - Offline Setup**: [`JETSON_NANO_4GB_SETUP.md`](JETSON_NANO_4GB_SETUP.md) - Complete guide with Ollama (offline mode)
- **Jetson Nano - Cloud Setup**: [`JETSON_NANO_CLOUD_SETUP.md`](JETSON_NANO_CLOUD_SETUP.md) - Setup with OpenAI (cloud mode, no Ollama)
- **Cloud Deployment**: [`CLOUD_DEPLOYMENT_GUIDE.md`](CLOUD_DEPLOYMENT_GUIDE.md) - Deploy to cloud and hybrid architectures
- **Quick Reference**: [`JETSON_NANO_QUICK_REFERENCE.md`](JETSON_NANO_QUICK_REFERENCE.md) - Common commands and troubleshooting
- **Offline Setup**: [`SETUP_OFFLINE.md`](SETUP_OFFLINE.md) - General offline mode setup
- **Speed Optimization**: [`backend/SPEED_OPTIMIZATION.md`](backend/SPEED_OPTIMIZATION.md) - Performance tuning guide

## License

MIT

