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
- Vite as build tool
- Tailwind CSS + shadcn/ui
- Zustand for state management
- React Hook Form + Zod
- Axios for HTTP requests

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your API URL
npm run dev
```

## Features

- AI-powered legal analysis with risk assessment
- Multilingual support (Hindi, English, Tamil, Telugu, Bengali, Marathi)
- Voice input/output using Whisper and TTS
- Document upload and analysis
- RAG-based knowledge retrieval
- User authentication and profiles
- Admin dashboard
- Legal aid center directory

## License

MIT

