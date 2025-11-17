# Setup Instructions

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- OpenAI API Key
- (Optional) AWS Account for S3 storage
- (Optional) Pinecone/Weaviate account for vector database

## Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration:
# - DATABASE_URL
# - REDIS_URL
# - OPENAI_API_KEY
# - SECRET_KEY (generate a secure random key)
# - PINECONE_API_KEY (if using Pinecone)
# - AWS credentials (if using S3)
```

5. Set up PostgreSQL database:
```bash
# Create database
createdb legal_db

# Or using psql:
psql -U postgres
CREATE DATABASE legal_db;
\q
```

6. Install pgvector extension:
```bash
psql -U postgres -d legal_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

7. Run database migrations:
```bash
alembic upgrade head
```

8. Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API docs at `http://localhost:8000/api/docs`

## Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env:
# VITE_API_URL=http://localhost:8000
```

4. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Database Schema

The database includes the following tables:
- `users` - User accounts
- `queries` - Legal queries submitted by users
- `ai_responses` - AI-generated responses to queries
- `feedback` - User feedback on responses
- `legal_aid_centers` - Legal aid center directory

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Development Notes

- The backend uses async/await throughout for high performance
- Frontend uses React 18 with TypeScript for type safety
- Authentication uses JWT tokens with refresh token mechanism
- AI analysis uses OpenAI GPT-4o with function calling for structured output
- RAG pipeline retrieves relevant legal context before AI analysis
- Multilingual support for Hindi, English, Tamil, Telugu, Bengali, Marathi

## Next Steps

1. Set up vector database (Pinecone or Weaviate)
2. Index legal documents in the knowledge base
3. Configure AWS S3 for file storage
4. Set up monitoring and logging
5. Deploy to production

