# AIDA Demo Application - Python Backend + Docker Implementation Guide

## 📋 Table of Contents
1. [Prerequisites & Environment Setup](#prerequisites--environment-setup)
2. [Docker Setup & Configuration](#docker-setup--configuration)
3. [Supabase Database Setup](#supabase-database-setup)
4. [Python Backend Development](#python-backend-development)
5. [Frontend Development (React)](#frontend-development-react)
6. [Docker Compose Configuration](#docker-compose-configuration)
7. [Authentication Setup (Clerk)](#authentication-setup-clerk)
8. [RAG System Implementation](#rag-system-implementation)
9. [Deployment & Testing](#deployment--testing)

---

## Prerequisites & Environment Setup

### Required Software Installation

```bash
# 1. Install Python 3.11+ (recommended)
# Download from https://python.org or use package manager

# Verify Python installation
python --version
pip --version

# 2. Install Docker Desktop
# Download from https://docker.com/products/docker-desktop/
# After installation, verify:
docker --version
docker-compose --version

# 3. Install Node.js 18+ (for frontend)
# Download from https://nodejs.org/
node --version
npm --version

# 4. Install Git
git --version

# 5. Install VS Code (recommended)
# Download from https://code.visualstudio.com/
```

### Required Accounts & API Keys
1. **GitHub Account** - For code repository
2. **Supabase Account** - For database and vector storage
3. **OpenAI Account** - For GPT API access
4. **Clerk Account** - For authentication
5. **Docker Hub Account** - For container registry (optional)

---

## Docker Setup & Configuration

### 1. Install Docker Desktop

**Windows/Mac:**
1. Download Docker Desktop from [docker.com](https://docker.com/products/docker-desktop/)
2. Run installer and follow setup wizard
3. Start Docker Desktop application
4. Verify installation:

```bash
docker run hello-world
```

**Linux (Ubuntu/Debian):**
```bash
# Update package database
sudo apt update

# Install Docker
sudo apt install docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
```

### 2. Create Docker Configuration Files

Create these files in your project root:

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./
RUN npm install

# Copy source code
COPY frontend/ .

# Build the app
RUN npm run build

# Serve the app
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Supabase Database Setup

### 1. Create Supabase Project

**Step-by-step Setup:**

1. **Sign up for Supabase:**
   - Go to [supabase.com](https://supabase.com)
   - Click "Start your project"
   - Sign up with GitHub (recommended)

2. **Create New Project:**
   - Click "New Project"
   - Choose your organization
   - Enter project name: `aida-demo`
   - Set database password (save this!)
   - Choose region (closest to your users)
   - Click "Create new project"
   - Wait 2-3 minutes for setup

3. **Get API Credentials:**
   - Go to Settings → API
   - Copy these values:
     - Project URL
     - Project API keys → `anon public`
     - Project API keys → `service_role` (keep secret!)

### 2. Enable Vector Extension & Create Schema

1. **Enable Vector Extension:**
   - Go to SQL Editor in Supabase dashboard
   - Click "New Query"
   - Run this SQL:

```sql
-- Enable the vector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;
```

2. **Create Database Tables:**

```sql
-- Create documents table for RAG system
CREATE TABLE documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI ada-002 embedding dimensions
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create index for fast similarity search
CREATE INDEX documents_embedding_idx ON documents 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create chat sessions table
CREATE TABLE chat_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create chat messages table
CREATE TABLE chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create function for similarity search
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) as similarity
    FROM documents
    WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Create conference data tables
CREATE TABLE conferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    location TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE TABLE speakers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conference_id UUID REFERENCES conferences(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    title TEXT,
    company TEXT,
    bio TEXT,
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE TABLE sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conference_id UUID REFERENCES conferences(id) ON DELETE CASCADE,
    speaker_id UUID REFERENCES speakers(id),
    title TEXT NOT NULL,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    location TEXT,
    track TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
```

3. **Set Row Level Security (RLS):**

```sql
-- Enable RLS on all tables
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE conferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE speakers ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access to conference data
CREATE POLICY "Public read access for conferences" ON conferences FOR SELECT USING (true);
CREATE POLICY "Public read access for speakers" ON speakers FOR SELECT USING (true);
CREATE POLICY "Public read access for sessions" ON sessions FOR SELECT USING (true);
CREATE POLICY "Public read access for documents" ON documents FOR SELECT USING (true);

-- Allow authenticated users to create chat sessions and messages
CREATE POLICY "Users can create chat sessions" ON chat_sessions FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can read own chat sessions" ON chat_sessions FOR SELECT USING (true);
CREATE POLICY "Users can create chat messages" ON chat_messages FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can read chat messages" ON chat_messages FOR SELECT USING (true);
```

---

## Python Backend Development

### 1. Create Backend Project Structure

```bash
# Create project directory
mkdir aida-demo-app
cd aida-demo-app

# Create backend structure
mkdir backend
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Create directory structure
mkdir app
mkdir app/api
mkdir app/core
mkdir app/services
mkdir app/models
mkdir app/utils
mkdir tests
```

### 2. Install Python Dependencies

```bash
# Create requirements.txt
touch requirements.txt
```

Add these dependencies to `requirements.txt`:

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
supabase==2.3.0
openai==1.3.0
python-multipart==0.0.6
httpx==0.25.2
pandas==2.1.4
numpy==1.25.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
aiofiles==23.2.1
python-json-logger==2.0.7
pgvector==0.2.4
asyncpg==0.29.0
sqlalchemy==2.0.23
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Create Core Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App settings
    app_name: str = "AIDA Conference Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API settings
    api_v1_str: str = "/api/v1"
    
    # Database
    supabase_url: str
    supabase_key: str
    supabase_service_role_key: str
    
    # OpenAI
    openai_api_key: str
    
    # Authentication
    clerk_secret_key: Optional[str] = None
    
    # CORS
    backend_cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://localhost:3000",
        "https://localhost:8080",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 4. Create Database Service

```python
# app/services/database.py
from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key  # Use service role for backend operations
        )
    
    async def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            response = self.supabase.table('conferences').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def create_document(self, content: str, embedding: list, metadata: dict = None) -> str:
        """Store a document with its embedding"""
        try:
            data = {
                'content': content,
                'embedding': embedding,
                'metadata': metadata or {}
            }
            
            response = self.supabase.table('documents').insert(data).execute()
            return response.data[0]['id']
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise
    
    async def search_documents(self, query_embedding: list, threshold: float = 0.7, limit: int = 5):
        """Search for similar documents using vector similarity"""
        try:
            response = self.supabase.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_count': limit
                }
            ).execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    async def create_chat_session(self, user_id: str = None) -> str:
        """Create a new chat session"""
        try:
            data = {'user_id': user_id} if user_id else {}
            
            response = self.supabase.table('chat_sessions').insert(data).execute()
            return response.data[0]['id']
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            raise
    
    async def save_chat_message(self, session_id: str, role: str, content: str, metadata: dict = None):
        """Save a chat message"""
        try:
            data = {
                'session_id': session_id,
                'role': role,
                'content': content,
                'metadata': metadata or {}
            }
            
            response = self.supabase.table('chat_messages').insert(data).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error saving chat message: {e}")
            raise

# Global database instance
db = DatabaseService()
```

### 5. Create OpenAI Service

```python
# app/services/openai_service.py
from openai import AsyncOpenAI
from app.core.config import settings
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text using OpenAI"""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise
    
    async def generate_chat_response(
        self, 
        messages: List[Dict[str, str]], 
        context: List[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Generate chat response using GPT"""
        try:
            # Build system prompt with context
            system_content = """You are AIDA, a helpful AI assistant for a technology conference. 
You provide information about sessions, speakers, schedules, and conference logistics.

Guidelines:
- Be friendly, professional, and concise
- Use specific information from the context when available
- If you don't know something, say so politely
- Focus on conference-related topics
- Provide actionable information when possible"""

            if context:
                system_content += f"\n\nRelevant information:\n" + "\n".join(context)
            
            # Prepare messages
            chat_messages = [
                {"role": "system", "content": system_content}
            ] + messages
            
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=chat_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            raise

# Global OpenAI service instance
openai_service = OpenAIService()
```

### 6. Create RAG Service

```python
# app/services/rag_service.py
from app.services.database import db
from app.services.openai_service import openai_service
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.db = db
        self.openai = openai_service
    
    async def process_and_store_content(self, content: str, metadata: dict = None) -> str:
        """Process content, create embedding, and store in database"""
        try:
            # Create embedding
            embedding = await self.openai.create_embedding(content)
            
            # Store in database
            doc_id = await self.db.create_document(content, embedding, metadata)
            
            logger.info(f"Stored document with ID: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Error processing content: {e}")
            raise
    
    async def search_relevant_content(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for relevant content based on query"""
        try:
            # Create query embedding
            query_embedding = await self.openai.create_embedding(query)
            
            # Search similar documents
            results = await self.db.search_documents(query_embedding, limit=limit)
            
            return results
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            raise
    
    async def generate_contextual_response(
        self, 
        user_message: str, 
        chat_history: List[Dict[str, str]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, any]:
        """Generate response using RAG approach"""
        try:
            # Search for relevant context
            relevant_docs = await self.search_relevant_content(user_message)
            context = [doc['content'] for doc in relevant_docs]
            
            # Prepare chat messages
            messages = chat_history or []
            messages.append({"role": "user", "content": user_message})
            
            # Generate response
            response = await self.openai.generate_chat_response(
                messages=messages,
                context=context
            )
            
            # Save to database if session provided
            if session_id:
                await self.db.save_chat_message(session_id, "user", user_message)
                await self.db.save_chat_message(session_id, "assistant", response)
            
            return {
                "response": response,
                "context": relevant_docs,
                "sources": [doc.get('metadata', {}) for doc in relevant_docs]
            }
        except Exception as e:
            logger.error(f"Error generating contextual response: {e}")
            raise

# Global RAG service instance
rag_service = RAGService()
```

### 7. Create API Routes

```python
# app/api/chat.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.rag_service import rag_service
from app.services.database import db
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    context: List[Dict]
    timestamp: str

@router.post("/chat", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message to AIDA and get response"""
    try:
        # Create session if not provided
        session_id = request.session_id
        if not session_id:
            session_id = await db.create_chat_session(request.user_id)
        
        # Generate response using RAG
        result = await rag_service.generate_contextual_response(
            user_message=request.message,
            session_id=session_id
        )
        
        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            context=result["context"],
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/chat/sessions/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        response = db.supabase.table('chat_messages')\
            .select('*')\
            .eq('session_id', session_id)\
            .order('created_at')\
            .execute()
        
        return {"messages": response.data}
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")
```

### 8. Create Main Application

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import chat
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix=f"{settings.api_v1_str}", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "AIDA Conference Assistant API", "version": settings.app_version}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.services.database import db
    
    db_healthy = await db.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "version": settings.app_version
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)
```

### 9. Create Environment File

```bash
# backend/.env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
OPENAI_API_KEY=your_openai_api_key
DEBUG=True
```

---

## Docker Compose Configuration

### Create Docker Compose File

```yaml
# docker-compose.yml (in project root)
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=True
    volumes:
      - ./backend:/app
    depends_on:
      - db
    networks:
      - aida-network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - aida-network

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: aida_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - aida-network

volumes:
  postgres_data:

networks:
  aida-network:
    driver: bridge
```

### Development Docker Compose

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=True
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - aida-network

networks:
  aida-network:
    driver: bridge
```

### Running with Docker

```bash
# Development mode (with hot reload)
docker-compose -f docker-compose.dev.yml up --build

# Production mode
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Clean up everything (including volumes)
docker-compose down -v
```

---

## Testing the Setup

### 1. Test Backend API

```bash
# Start backend
cd backend
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
uvicorn main:app --reload

# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what is this conference about?"}'
```

### 2. Load Sample Conference Data

```python
# scripts/load_sample_data.py
import asyncio
from app.services.rag_service import rag_service

async def load_sample_data():
    """Load sample conference data"""
    
    # Sample conference information
    conference_info = [
        {
            "content": "TechConf 2024 is a cutting-edge technology conference featuring AI, machine learning, cloud computing, and software development. The conference runs from March 15-17, 2024 in San Francisco.",
            "metadata": {"type": "conference", "category": "general"}
        },
        {
            "content": "Keynote Session: 'The Future of AI' by Dr. Sarah Chen, Chief AI Officer at TechCorp. March 15, 9:00 AM - 10:00 AM, Main Auditorium. Dr. Chen will discuss the latest developments in artificial intelligence and machine learning.",
            "metadata": {"type": "session", "speaker": "Dr. Sarah Chen", "time": "March 15, 9:00 AM"}
        },
        {
            "content": "Workshop: 'Building Scalable APIs with FastAPI' by Mike Johnson, Senior Developer at CloudTech. March 16, 2:00 PM - 4:00 PM, Room B. Hands-on workshop covering FastAPI development, testing, and deployment.",
            "metadata": {"type": "workshop", "speaker": "Mike Johnson", "time": "March 16, 2:00 PM"}
        }
    ]
    
    for item in conference_info:
        doc_id = await rag_service.process_and_store_content(
            content=item["content"],
            metadata=item["metadata"]
        )
        print(f"Stored document: {doc_id}")

if __name__ == "__main__":
    asyncio.run(load_sample_data())
```

Run the script:
```bash
cd backend
python scripts/load_sample_data.py
```

---

This updated guide provides:

1. **Clear Docker setup** with step-by-step installation
2. **Python FastAPI backend** instead of Node.js
3. **Detailed Supabase configuration** with SQL scripts
4. **Complete development workflow** with Docker Compose
5. **Production-ready structure** with proper error handling
6. **Testing examples** and sample data loading

The setup uses modern Python async/await patterns, proper dependency injection, and follows FastAPI best practices. The Docker configuration supports both development (with hot reload) and production deployments.






















<!-- # AIDA Demo Application - Complete Implementation Guide

## 📋 Table of Contents
1. [Prerequisites & Environment Setup](#prerequisites--environment-setup)
2. [Project Structure Setup](#project-structure-setup)
3. [Frontend Development (React + AG UI)](#frontend-development-react--ag-ui)
4. [Backend Setup (Armada MCP)](#backend-setup-armada-mcp)
5. [Database Configuration (Supabase)](#database-configuration-supabase)
6. [RAG System Implementation](#rag-system-implementation)
7. [Authentication Setup (Clerk)](#authentication-setup-clerk)
8. [Admin Interface Development](#admin-interface-development)
9. [Integration & Testing](#integration--testing)
10. [Deployment (Vercel)](#deployment-vercel)
11. [Data Management & Content Upload](#data-management--content-upload)

---

## Prerequisites & Environment Setup

### Required Software
```bash
# Install Node.js (v18 or higher)
# Download from https://nodejs.org/

# Verify installation
node --version
npm --version

# Install pnpm (recommended package manager)
npm install -g pnpm

# Install Git
# Download from https://git-scm.com/
git --version
```

### Required Accounts & Services
1. **GitHub Account** - For code repository
2. **Vercel Account** - For hosting (sign up with GitHub)
3. **Supabase Account** - For database and vector storage
4. **Clerk Account** - For authentication
5. **OpenAI Account** - For GPT API access (or Anthropic for Claude)

### Development Environment
```bash
# Install VS Code extensions (recommended)
# - ES7+ React/Redux/React-Native snippets
# - Tailwind CSS IntelliSense
# - Prettier - Code formatter
# - ESLint
```

---

## Project Structure Setup

### 1. Create Project Repository
```bash
# Create new directory
mkdir aida-demo-app
cd aida-demo-app

# Initialize Git repository
git init
git branch -M main

# Create GitHub repository (via GitHub CLI or web interface)
gh repo create aida-demo-app --public --push --source=.
```

### 2. Initialize React Project
```bash
# Create React app with TypeScript
npx create-react-app frontend --template typescript
cd frontend

# Install additional dependencies
pnpm install @radix-ui/react-dialog @radix-ui/react-button @radix-ui/react-input
pnpm install @radix-ui/react-scroll-area @radix-ui/react-toast
pnpm install tailwindcss postcss autoprefixer
pnpm install axios react-query
pnpm install @types/node

# Initialize Tailwind CSS
npx tailwindcss init -p
```

### 3. Configure Tailwind CSS
```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [],
}
```

### 4. Create Project Structure
```bash
# In project root
mkdir backend
mkdir docs
mkdir scripts

# Frontend structure
cd frontend/src
mkdir components
mkdir pages
mkdir hooks
mkdir utils
mkdir types
mkdir services

# Create component directories
cd components
mkdir ui
mkdir chat
mkdir admin
mkdir layout
```

---

## Frontend Development (React + AG UI)

### 1. Create Base Components

#### UI Components
```typescript
// src/components/ui/Button.tsx
import React from 'react';
import { cn } from '../../utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
}

export const Button: React.FC<ButtonProps> = ({
  className,
  variant = 'primary',
  size = 'md',
  ...props
}) => {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-md font-medium transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        {
          'bg-primary-600 text-white hover:bg-primary-700': variant === 'primary',
          'bg-gray-100 text-gray-900 hover:bg-gray-200': variant === 'secondary',
          'border border-gray-300 bg-transparent hover:bg-gray-50': variant === 'outline',
        },
        {
          'h-8 px-3 text-sm': size === 'sm',
          'h-10 px-4': size === 'md',
          'h-12 px-6 text-lg': size === 'lg',
        },
        className
      )}
      {...props}
    />
  );
};
```

```typescript
// src/components/ui/Input.tsx
import React from 'react';
import { cn } from '../../utils/cn';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({
  className,
  label,
  error,
  ...props
}) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <input
        className={cn(
          'flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2',
          'text-sm placeholder:text-gray-400',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
          'disabled:cursor-not-allowed disabled:opacity-50',
          error && 'border-red-500 focus:ring-red-500',
          className
        )}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};
```

#### Chat Components
```typescript
// src/components/chat/ChatMessage.tsx
import React from 'react';
import { cn } from '../../utils/cn';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp: Date;
  isLoading?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isUser,
  timestamp,
  isLoading = false,
}) => {
  return (
    <div className={cn(
      'flex w-full mb-4',
      isUser ? 'justify-end' : 'justify-start'
    )}>
      <div className={cn(
        'max-w-[80%] rounded-lg px-4 py-2',
        isUser 
          ? 'bg-primary-600 text-white' 
          : 'bg-gray-100 text-gray-900'
      )}>
        {isLoading ? (
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
          </div>
        ) : (
          <p className="text-sm leading-relaxed">{message}</p>
        )}
        <span className={cn(
          'text-xs opacity-70 mt-1 block',
          isUser ? 'text-blue-100' : 'text-gray-500'
        )}>
          {timestamp.toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
};
```

```typescript
// src/components/chat/ChatInput.tsx
import React, { useState, useRef } from 'react';
import { Button } from '../ui/Button';
import { Send } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Ask AIDA anything about the conference..."
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4 border-t bg-white">
      <textarea
        ref={textareaRef}
        value={message}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-3 text-sm
                   focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                   disabled:bg-gray-50 disabled:cursor-not-allowed
                   max-h-32 min-h-[48px]"
      />
      <Button
        type="submit"
        disabled={!message.trim() || disabled}
        size="lg"
        className="self-end"
      >
        <Send className="w-4 h-4" />
      </Button>
    </form>
  );
};
```

### 2. Create Main Chat Interface
```typescript
// src/components/chat/ChatInterface.tsx
import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { useChatMessages } from '../../hooks/useChatMessages';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi! I'm AIDA, your conference assistant. I can help you with information about the event, sessions, speakers, and more. What would you like to know?",
      isUser: false,
      timestamp: new Date(),
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { sendMessage } = useChatMessages();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (messageText: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendMessage(messageText);
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response,
        isUser: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-primary-50">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold">AI</span>
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">AIDA</h2>
            <p className="text-sm text-gray-600">Conference Assistant</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span className="text-sm text-gray-600">Online</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message.text}
            isUser={message.isUser}
            timestamp={message.timestamp}
          />
        ))}
        {isLoading && (
          <ChatMessage
            message=""
            isUser={false}
            timestamp={new Date()}
            isLoading={true}
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput
        onSendMessage={handleSendMessage}
        disabled={isLoading}
      />
    </div>
  );
};
```

### 3. Create Custom Hooks
```typescript
// src/hooks/useChatMessages.ts
import { useState } from 'react';
import { chatService } from '../services/chatService';

export const useChatMessages = () => {
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (message: string): Promise<string> => {
    setIsLoading(true);
    try {
      const response = await chatService.sendMessage(message);
      return response.message;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    sendMessage,
    isLoading,
  };
};
```

### 4. Create Services
```typescript
// src/services/chatService.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:3001';

interface ChatResponse {
  message: string;
  context?: any;
}

class ChatService {
  private apiClient = axios.create({
    baseURL: `${API_BASE_URL}/api`,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  async sendMessage(message: string): Promise<ChatResponse> {
    const response = await this.apiClient.post('/chat', {
      message,
      timestamp: new Date().toISOString(),
    });
    
    return response.data;
  }

  async uploadDocument(file: File): Promise<{ success: boolean; id: string }> {
    const formData = new FormData();
    formData.append('document', file);

    const response = await this.apiClient.post('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }
}

export const chatService = new ChatService();
```

### 5. Create Main App Component
```typescript
// src/App.tsx
import React from 'react';
import { ChatInterface } from './components/chat/ChatInterface';
import './App.css';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto h-screen max-h-[800px]">
        <div className="mb-6 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AIDA Conference Demo
          </h1>
          <p className="text-gray-600">
            Your AI-powered conference assistant
          </p>
        </div>
        
        <div className="h-[calc(100%-120px)]">
          <ChatInterface />
        </div>
      </div>
    </div>
  );
}

export default App;
```

---

## Backend Setup (Armada MCP)

### 1. Initialize Backend Project
```bash
# In project root
cd backend

# Initialize Node.js project
npm init -y

# Install dependencies
pnpm install express cors helmet morgan
pnpm install @types/express @types/cors @types/node
pnpm install typescript ts-node nodemon
pnpm install dotenv
pnpm install @supabase/supabase-js
pnpm install openai
pnpm install multer @types/multer
```

### 2. Configure TypeScript
```json
// backend/tsconfig.json
{
  "compilerOptions": {
    "target": "es2020",
    "module": "commonjs",
    "lib": ["es2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### 3. Create Backend Structure
```bash
mkdir src
cd src
mkdir controllers
mkdir services
mkdir middleware
mkdir types
mkdir utils
mkdir routes
```

### 4. Create MCP Core Setup
```typescript
// backend/src/types/index.ts
export interface MCPRequest {
  method: string;
  params: any;
  id: string;
}

export interface MCPResponse {
  result?: any;
  error?: {
    code: number;
    message: string;
  };
  id: string;
}

export interface ConferenceData {
  id: string;
  title: string;
  description: string;
  schedule: SessionData[];
  speakers: SpeakerData[];
  locations: LocationData[];
}

export interface SessionData {
  id: string;
  title: string;
  description: string;
  speaker: string;
  time: string;
  location: string;
  track: string;
}

export interface SpeakerData {
  id: string;
  name: string;
  title: string;
  company: string;
  bio: string;
  sessions: string[];
}

export interface LocationData {
  id: string;
  name: string;
  description: string;
  capacity: number;
  floor: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}
```

### 5. Create RAG Service
```typescript
// backend/src/services/ragService.ts
import { createClient } from '@supabase/supabase-js';
import OpenAI from 'openai';
import { ConferenceData, ChatMessage } from '../types';

export class RAGService {
  private supabase;
  private openai;

  constructor() {
    this.supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_ANON_KEY!
    );
    
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
  }

  async embedText(text: string): Promise<number[]> {
    const response = await this.openai.embeddings.create({
      model: 'text-embedding-ada-002',
      input: text,
    });
    
    return response.data[0].embedding;
  }

  async storeDocument(content: string, metadata: any): Promise<string> {
    const embedding = await this.embedText(content);
    
    const { data, error } = await this.supabase
      .from('documents')
      .insert({
        content,
        embedding,
        metadata,
        created_at: new Date().toISOString(),
      })
      .select()
      .single();

    if (error) throw error;
    return data.id;
  }

  async searchSimilarDocuments(query: string, limit: number = 5): Promise<any[]> {
    const queryEmbedding = await this.embedText(query);
    
    const { data, error } = await this.supabase.rpc('match_documents', {
      query_embedding: queryEmbedding,
      match_threshold: 0.7,
      match_count: limit,
    });

    if (error) throw error;
    return data || [];
  }

  async generateResponse(
    messages: ChatMessage[],
    context: string[]
  ): Promise<string> {
    const systemPrompt = `You are AIDA, a helpful AI assistant for a technology conference. 
Use the following context to answer questions about the conference, sessions, speakers, and logistics.

Context:
${context.join('\n\n')}

Guidelines:
- Be friendly and professional
- Provide specific information when available
- If you don't know something, say so politely
- Focus on conference-related topics
- Keep responses concise but informative`;

    const completion = await this.openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        { role: 'system', content: systemPrompt },
        ...messages.map(msg => ({
          role: msg.role,
          content: msg.content,
        })),
      ],
      max_tokens: 500,
      temperature: 0.7,
    });

    return completion.choices[0]?.message?.content || 'I apologize, but I couldn\'t generate a response right now.';
  }

  async processConferenceData(data: ConferenceData): Promise<void> {
    // Store conference overview
    await this.storeDocument(
      `Conference: ${data.title}. ${data.description}`,
      { type: 'conference', id: data.id }
    );

    // Store sessions
    for (const session of data.schedule) {
      const content = `Session: ${session.title}. 
Description: ${session.description}. 
Speaker: ${session.speaker}. 
Time: ${session.time}. 
Location: ${session.location}. 
Track: ${session.track}`;
      
      await this.storeDocument(content, {
        type: 'session',
        id: session.id,
        speaker: session.speaker,
        time: session.time,
      });
    }

    // Store speakers
    for (const speaker of data.speakers) {
      const content = `Speaker: ${speaker.name}, ${speaker.title} at ${speaker.company}. 
Bio: ${speaker.bio}. 
Sessions: ${speaker.sessions.join(', ')}`;
      
      await this.storeDocument(content, {
        type: 'speaker',
        id: speaker.id,
        name: speaker.name,
      });
    }

    // Store locations
    for (const location of data.locations) {
      const content = `Location: ${location.name}. 
Description: ${location.description}. 
Capacity: ${location.capacity}. 
Floor: ${location.floor}`;
      
      await this.storeDocument(content, {
        type: 'location',
        id: location.id,
        name: location.name,
      });
    }
  }
}
```

### 6. Create Chat Controller
```typescript
// backend/src/controllers/chatController.ts
import { Request, Response } from 'express';
import { RAGService } from '../services/ragService';
import { ChatMessage } from '../types';

export class ChatController {
  private ragService: RAGService;

  constructor() {
    this.ragService = new RAGService();
  }

  async sendMessage(req: Request, res: Response): Promise<void> {
    try {
      const { message, sessionId } = req.body;

      if (!message || typeof message !== 'string') {
        res.status(400).json({
          error: 'Message is required and must be a string',
        });
        return;
      }

      // Search for relevant context
      const relevantDocs = await this.ragService.searchSimilarDocuments(message);
      const context = relevantDocs.map(doc => doc.content);

      // Create messages array
      const messages: ChatMessage[] = [
        {
          role: 'user',
          content: message,
          timestamp: new Date(),
        },
      ];

      // Generate AI response
      const response = await this.ragService.generateResponse(messages, context);

      res.json({
        message: response,
        context: relevantDocs.map(doc => ({
          type: doc.metadata?.type,
          score: doc.similarity,
        })),
      });
    } catch (error) {
      console.error('Chat error:', error);
      res.status(500).json({
        error: 'Internal server error',
      });
    }
  }

  async uploadData(req: Request, res: Response): Promise<void> {
    try {
      const conferenceData = req.body;

      await this.ragService.processConferenceData(conferenceData);

      res.json({
        success: true,
        message: 'Conference data uploaded successfully',
      });
    } catch (error) {
      console.error('Upload error:', error);
      res.status(500).json({
        error: 'Failed to upload conference data',
      });
    }
  }
}
```

### 7. Create Express Server
```typescript
// backend/src/app.ts
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import { ChatController } from './controllers/chatController';

dotenv.config();

const app = express();
const chatController = new ChatController();

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
}));
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// API routes
app.post('/api/chat', chatController.sendMessage.bind(chatController));
app.post('/api/data/upload', chatController.uploadData.bind(chatController));

// Error handling
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

const PORT = process.env.PORT || 3001;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### 8. Create Package Scripts
```json
// backend/package.json scripts section
{
  "scripts": {
    "dev": "nodemon src/app.ts",
    "build": "tsc",
    "start": "node dist/app.js",
    "test": "jest"
  }
}
```

---

## Database Configuration (Supabase)

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Choose organization and enter project details
4. Wait for project to be created (2-3 minutes)
5. Copy Project URL and anon key from Settings > API

### 2. Enable Vector Extension
```sql
-- In Supabase SQL Editor, run:
create extension if not exists vector;
```

### 3. Create Database Schema
```sql
-- Create documents table with vector embeddings
create table documents (
  id uuid default gen_random_uuid() primary key,
  content text not null,
  embedding vector(1536), -- OpenAI ada-002 dimensions
  metadata jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create index for similarity search
create index on documents using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

-- Create function for similarity search
create or replace function match_documents (
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language sql stable
as $$
  select
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where 1 - (documents.embedding <=> query_embedding) > match_threshold
  order by documents.embedding <=> query_embedding
  limit match_count;
$$;
```

### 4. Create Environment Variables
```bash
# backend/.env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key
FRONTEND_URL=http://localhost:3000
PORT=3001
```

---

## Authentication Setup (Clerk)

### 1. Create Clerk Application
1. Go to [clerk.com](https://clerk.com)
2. Sign up and create new application
3. Choose authentication methods (email/password, social logins)
4. Copy publishable key and secret key
# MCP-RAG-Demo










 -->




## 🎯 Project Overview

This project is a tablet-optimized React application built for Vant4ge to demo AIDA, an AI assistant, at an upcoming conference. It uses Retrieval-Augmented Generation (RAG) and the Armada MCP backend to intelligently answer questions about the event.

The app is styled using AG UI, hosted on Vercel, and leverages Supabase and Clerk for backend services and authentication.

---

## 🧱 Architecture Overview

### 🔹 Frontend
- **Framework**: React
- **Styling**: AG UI
- **Auth**: Clerk
- **Hosting**: Vercel

### 🔹 Backend (MCP Layer)
- Built on **Armada's MCP framework**
- Powered by **RAG**
- Data includes:
  - Conference schedule/logistics
  - AIDA demo content
  - Scripted responses
- Vector DB: **Supabase Edge Functions / Postgres + pgvector**
- Guardrails + Tooling managed by MCP

---

## 📲 Core Features (MVP Scope)

### 1. AI Chat Interface
- Conversational UI powered by GPT-4o or Claude 3
- Text interaction + scripted responses
- FAQs + Schedule + Product Questions

### 2. RAG-Powered Backend
- Ingests structured metadata (CSV, JSON, Airtable)
- Uses MCP schema to process and respond
- Logs queries and tracks basic analytics

### 3. Admin Interface
- Authenticated access to upload structured data

---

## 🔄 Tech Stack

| Layer        | Tooling                                |
|--------------|----------------------------------------|
| Hosting      | Vercel                                 |
| Auth         | Supabase (POC) → Clerk (Production)    |
| DB / Vector  | Supabase with Postgres + pgvector      |
| Frontend     | React + AG UI                          |
| AI Model     | GPT-4o or Claude 3 (via API)           |
| Backend      | Armada MCP Core                        |

---

## 📋 Step-by-Step Setup & Implementation Guide

### ✅ Step 1: Frontend Setup

1. Create the React app:

```bash
npx create-react-app mcp-rag-demo --template typescript
cd mcp-rag-demo










<!-- 
A demo project showcasing a **tablet-optimized React application** powered by an **Armada MCP (Model Context Protocol) backend** with **Retrieval-Augmented Generation (RAG)**. Conference attendees interact with **AIDA**, our AI assistant, to ask questions about the event, demo experience, and product features.

---

## 📖 **Table of Contents**
- [Project Vision](#project-vision)
- [Architecture Overview](#architecture-overview)
- [Core Features (MVP)](#core-features-mvp)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Clone & Install](#clone--install)
  - [Running the Backend](#running-the-backend)
  - [Running the Frontend](#running-the-frontend)
  - [Running Tests](#running-tests)
- [Branching Strategy](#branching-strategy)
- [Sprint 1 Deliverables & Timeline](#sprint-1-deliverables--timeline)
- [Epic & User Stories](#epic--user-stories)
- [Future Roadmap](#future-roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 **Project Vision**
_As a conference attendee, I want to interact with AIDA through an intuitive tablet interface so that I can learn about the conference, demo capabilities, and product features in an engaging conversational experience._

---

## 🏗 **Architecture Overview**

### **Frontend**
- **React** app optimized for **iPad/Android tablets**
- **Component Library:** AG UI
- **Hosting:** Vercel
- **Auth:** Clerk (admin/preview access)

### **Backend (MCP Layer)**
- **Framework:** FastAPI + Docker
- **MCP Core:** Armada’s MCP framework
- **RAG Knowledge Base:**
  - Conference schedule & logistics
  - AIDA demo details
  - Scripted conversation flows
- **Vector Store:** Supabase (Postgres + pgvector or Edge Functions)
- **Logging & Analytics:** Basic interaction tracking

---

## 🌟 **Core Features (MVP)**

### **1. AI Chat Interface**
- Conversational UI powered by **GPT-4o** or **Claude 3**
- Text-based interaction with optional scripted responses
- Answers include:
  - Event schedule, locations, sessions
  - AIDA feature info & technical background
  - FAQs curated by Vant4ge

### **2. MCP-Driven RAG Backend**
- Ingest conference metadata (JSON/CSV/Airtable)
- Tooling support defined via MCP schema
- Logging + basic analytics

### **3. Basic Admin Interface**
- Secure file upload (JSON/CSV) for conference data
- Clerk-protected access for Vant4ge/Banyan teams

---

## 🔧 **Tech Stack**

| Layer            | Technology                          |
|-----------------|------------------------------------|
| **Frontend**    | React + AG UI                      |
| **Hosting**     | Vercel                             |
| **Auth**        | Clerk                              |
| **Backend (MCP)** | FastAPI + Armada MCP Core       |
| **Database**    | Supabase (Postgres + pgvector)     |
| **AI Model**    | GPT-4o / Claude 3 (via API)        |
| **Containerization** | Docker                        |
| **Testing**     | Pytest + FastAPI TestClient        |

---

## 🚀 **Getting Started**

### **Prerequisites**
- Node.js ≥ 18
- Python ≥ 3.10
- Docker & Docker Compose
- Git

### **Environment Variables**
Create a `.env` in the root (backend) and `.env.local` in `frontend/`:

```env
# backend/.env
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
# any other MCP/Armada settings

# frontend/.env.local
NEXT_PUBLIC_SUPABASE_URL=https://xyz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...


Clone & Install
# Clone repo
git clone https://github.com/SNoeCode/mcp-rag-demo.git
cd mcp-rag-demo

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..


Running the Backend
docker build -t mcp-rag-backend .
docker run -p 8000:8000 --env-file .env mcp-rag-backend


- Health Check: GET http://localhost:8000/health
- MCP Health:   GET http://localhost:8000/mcp/health-mcp
Running the Frontend
cd frontend
npm run dev


- Open your tablet-simulated browser at: http://localhost:3000
Running Tests
# Run FastAPI backend tests
pytest --maxfail=1 --disable-warnings -q

# Run any React frontend tests (if added)
cd frontend && npm test



🔀 Branching Strategy
- main → Production-ready, updated only when merging develop
- develop → Integration branch for all new work
- feature/* → New features branch off develop
- bugfix/* → Bug fixes branch off develop
- hotfix/* → Urgent fixes branch off develop
- release/* → (Optional) Version branches off develop for QA before merging into main

📅 Sprint 1 Deliverables & Timeline
| Week | Days | Goals / Tasks | 
| 1 | Days 1–2 | Setup FastAPI, Docker, Supabase connection | 
|  | Days 3–4 | Scaffold React + AG UI chat interface with dummy messaging | 
|  | Day 5 | Implement MCP endpoint (basic schema) + health check | 
| 2 | Days 1–2 | Load sample conference/AIDA data into Supabase; build RAG retrieval logic | 
|  | Days 3–4 | Connect frontend → backend; run integration tests | 
|  | Day 5 | Build basic admin interface; finalize testing; prepare for sprint review | 



🌍 Future Roadmap
- Voice chat integration (Whisper / streaming)
- Multi-session management & engagement tracking
- Live data updates via CMS/Airtable webhooks
- Analytics dashboard (top queries, usage trends)
- Multiple conference profiles via MCP “profiles”

🤝 Contributing
- Fork the repo & clone locally
- Create a branch off develop (e.g. feature/awesome-thing)
- Make your changes & write tests
- Push & open a PR → develop
- After review, merge & delete your branch

📜 License
MIT © SNoeCode Feel free to adapt and extend this demo for your own RAG + MCP experiments!

Save this as **README.md** in your repo. 🚀 Let me know if anything needs tweaking!


📌 Steps to Save the README File
- Copy the markdown content below
- Create a new file in your repository
cd path/to/mcp-rag-demo
touch README.md
- Open the file in a text editor (VS Code, Nano, Vim, etc.)
nano README.md
- Paste the markdown content
- Save the file, commit, and push it to GitHub
git add README.md
git commit -m "docs: add detailed README"
git push origin develop



📜 Full README.md File (Copy-Paste Below)
# MCP-RAG-Demo

A demo project showcasing a **tablet-optimized React application** powered by an **Armada MCP (Model Context Protocol) backend** with **Retrieval-Augmented Generation (RAG)**. Conference attendees interact with **AIDA**, our AI assistant, to ask questions about the event, demo experience, and product features.

---

## 📖 **Table of Contents**
- [Project Vision](#project-vision)
- [Epic Breakdown](#epic-breakdown)
- [Sprint 1 User Stories](#sprint-1-user-stories)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Clone & Install](#clone--install)
  - [Running the Backend](#running-the-backend)
  - [Running the Frontend](#running-the-frontend)
  - [Running Tests](#running-tests)
- [Branching Strategy](#branching-strategy)
- [Sprint 1 Timeline](#sprint-1-timeline)
- [Success Metrics](#success-metrics)
- [Future Roadmap](#future-roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 **Project Vision**
_As a conference attendee, I want to interact with AIDA through an intuitive tablet interface so that I can learn about the conference, demo capabilities, and product features in an engaging conversational experience._

---

## 📋 **Epic Breakdown**
### **Epic 1: Core Chat Experience**
**Goal:** Deliver a functional chat interface that conference attendees can use to interact with AIDA.

### **Epic 2: RAG-Powered Knowledge System**
**Goal:** Implement intelligent responses using conference and product data.

### **Epic 3: Admin Content Management**
**Goal:** Enable Vant4ge team to manage and upload demo content.

### **Epic 4: Technical Foundation**
**Goal:** Establish robust, scalable technical infrastructure.

---

## 🏃‍♂️ **Sprint 1 User Stories**

### **Epic 1: Core Chat Experience**
#### **Story 1.1: Basic Chat Interface**
**Goal:** Create a clean, tablet-optimized chat interface.

#### **Acceptance Criteria**
✅ Chat interface displays properly on tablet screens (10-13 inches)  
✅ Input field is easily accessible and responsive to touch  
✅ Message history scrolls smoothly  
✅ Uses reusable UI components for consistent styling  
✅ Interface is intuitive without training  

#### **Tasks & Step-by-Step Instructions**
##### **1️⃣ Set Up React Project**
```bash
cd frontend
npx create-react-app chat-ui
cd chat-ui
npm install react-router-dom styled-components
npm start


2️⃣ Research Reusable Component Libraries
- AG UI (your project’s standard UI library)
- Material-UI (MUI) → npm install @mui/material @emotion/react @emotion/styled
- React Native Web (for touch optimization) → npm install react-native-web
- Styled Components → npm install styled-components
3️⃣ Create Responsive Chat Container Component
import React from "react";
import styled from "styled-components";

const ChatWrapper = styled.div`
  width: 100%;
  max-width: 800px;
  height: 80vh;
  display: flex;
  flex-direction: column;
  border-radius: 10px;
  background: #f5f5f5;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const MessageHistory = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 10px;
`;

const ChatContainer = () => {
  return (
    <ChatWrapper>
      <MessageHistory>
        {/* Messages will go here */}
      </MessageHistory>
    </ChatWrapper>
  );
};

export default ChatContainer;


4️⃣ Implement Message Input Component
import React, { useState } from "react";
import styled from "styled-components";

const InputWrapper = styled.div`
  display: flex;
  padding: 10px;
  background: white;
  border-top: 1px solid #ddd;
`;

const InputField = styled.input`
  flex: 1;
  padding: 12px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
  outline: none;
`;

const SendButton = styled.button`
  margin-left: 10px;
  padding: 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
`;

const MessageInput = ({ onSend }) => {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim() !== "") {
      onSend(message);
      setMessage("");
    }
  };

  return (
    <InputWrapper>
      <InputField
        type="text"
        placeholder="Type a message..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <SendButton onClick={handleSend}>Send</SendButton>
    </InputWrapper>
  );
};

export default MessageInput;


5️⃣ Add Scroll Behavior for Message History
const MessageHistory = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  scroll-behavior: smooth;
`;


6️⃣ Test on Multiple Tablet Screen Sizes
- Use Chrome DevTools:
- Open the app in Chrome.
- Right-click → Inspect → Toggle Device Toolbar.
- Select iPad Pro (11-inch, 12.9-inch) and Samsung Galaxy Tab S7.

📅 Sprint 1 Timeline
| Week | Days | Goals / Tasks | 
| 1 | Days 1–2 | Setup FastAPI, Docker, Supabase connection | 
|  | Days 3–4 | Scaffold React + AG UI chat interface with dummy messaging | 
|  | Day 5 | Implement MCP endpoint (basic schema) + health check | 
| 2 | Days 1–2 | Load sample conference/AIDA data into Supabase; build RAG retrieval logic | 
|  | Days 3–4 | Connect frontend → backend; run integration tests | 
|  | Day 5 | Build basic admin interface; finalize testing; prepare for sprint review | 



🚀 Success Metrics
✅ Response time < 3 seconds for 95% of queries
✅ Zero critical security vulnerabilities
✅ 99% uptime during demo period
✅ Mobile/tablet performance score > 90

🤝 Contributing
- Fork the repo & clone locally
- Create a branch off develop (e.g. feature/chat-ui)
- Make your changes & write tests
- Push & open a PR → develop
- After review, merge & delete your branch

📜 License
MIT © SNoeCode
Feel free to adapt and extend this demo for your own RAG + MCP experiments!

---

### **✅ Final Steps**
1. **Save this markdown content as `README.md`**  
2. **Commit & push it to GitHub**  
3. **Open your repo, and GitHub will format everything correctly**  

🚀 **Your README is now fully detailed and ready to go!**









# MCP-RAG-Demo

## 🎯 Project Overview

We are building a tablet-optimized React application for Vant4ge to demo AIDA, our AI assistant, at an upcoming conference. The goal is to provide a scripted and intelligent experience where attendees can interact with AIDA and ask questions about the conference, the demo, and the product experience.

The backend is powered by Armada's MCP layer, using Retrieval-Augmented Generation (RAG) to feed the AI with curated data and context. The front end uses AG UI components and leverages Supabase, Clerk, and Vercel for backend, auth, and hosting infrastructure.

## 🧱 Architecture Overview

### 🔹 Frontend

* React App (tablet-optimized)
* Component library: AG UI
* Hosted on Vercel
* Auth via Clerk

### 🔹 Backend (MCP Layer)

* Built on Armada MCP framework (FastAPI + Docker)
* RAG-powered knowledge base:

  * Conference schedule & logistics
  * AIDA demo experience (Vant4ge)
  * Scripted conversation flow
* Vector DB: Supabase (pgvector)
* Tooling defined via MCP concepts

---

## 🚧 Epics & Detailed Implementation Guide

### 🧩 Epic 1: Core Chat Experience

#### 1.1 Tablet-optimized UI Layout

* Install dependencies:

```bash
npx create-react-app mcp-rag-demo --template typescript
cd mcp-rag-demo
npm install ag-ui clerk-sdk react-router-dom
```

* Build responsive layout in `App.tsx`:

```tsx
import { Container, Header, Footer } from "ag-ui";

function App() {
  return (
    <Container maxWidth="md">
      <Header title="Ask AIDA" />
      <Chat />
      <Footer content="Vant4ge Conference 2024" />
    </Container>
  );
}
```

#### 1.2 Basic Message Flow + Dummy RAG

* Create `Chat.tsx`:

```tsx
import { Input } from "ag-ui";
import { useState } from "react";

export const Chat = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    setMessages([...messages, { sender: "user", text: input }, { sender: "AIDA", text: "This is a dummy response." }]);
    setInput("");
  };

  return (
    <div className="chat-container">
      {messages.map((msg, i) => <div key={i}><b>{msg.sender}:</b> {msg.text}</div>)}
      <Input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()} />
    </div>
  );
};
```

---

### 🧩 Epic 2: Knowledge-Powered Backend

#### 2.1 MCP Base Schema + Endpoint

* Set up FastAPI server:

```bash
mkdir backend && cd backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn openai supabase
```

* Create `main.py`:

```py
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/query")
async def query(data: Query):
    return {"answer": f"Echoing your question: {data.question}"}
```

#### 2.2 Supabase + pgvector Pipeline

* SQL for vector table:

```sql
create extension if not exists vector;
create table docs (
  id uuid default uuid_generate_v4(),
  content text,
  embedding vector(1536)
);
```

* Insert from script:

```py
from openai import OpenAI
from supabase import create_client

openai.api_key = "OPENAI_API_KEY"
supabase = create_client("SUPABASE_URL", "SUPABASE_KEY")

embedding = openai.Embedding.create(input="Schedule info", model="text-embedding-ada-002")
supabase.table("docs").insert({"content": "Schedule info", "embedding": embedding["data"][0]["embedding"]}).execute()
```

#### 2.3 Upload Tooling (CSV/Airtable)

* Accept CSV in FastAPI:

```py
from fastapi import UploadFile

@app.post("/upload")
async def upload(file: UploadFile):
    content = await file.read()
    # parse CSV and embed
    return {"status": "uploaded"}
```

---

### 🧩 Epic 3: Admin Management

#### 3.1 Clerk-Gated Upload Interface

* Add ClerkProvider and upload UI:

```tsx
import { ClerkProvider, SignedIn, SignedOut, SignIn, useUser } from "@clerk/clerk-react";

const AdminUpload = () => {
  const { user } = useUser();
  const handleUpload = async (e) => {
    const file = e.target.files[0];
    const form = new FormData();
    form.append("file", file);
    await fetch("/upload", { method: "POST", body: form });
  };
  return user ? <input type="file" onChange={handleUpload} /> : null;
};
```

---

### 🧩 Epic 4: Dev Infrastructure

#### 4.1 Vercel Deploy + Domains

* Push to GitHub, connect repo to Vercel.
* Add ENV vars: `CLERK_KEY`, `SUPABASE_URL`, `OPENAI_KEY`.

#### 4.2 Containerization + CI

* Create Dockerfile:

```Dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

* Add CI/CD workflow via GitHub Actions.

---

## 🌍 Future Roadmap

* 🎤 Voice chat (Whisper, streaming)
* 🧠 Multi-session engagement memory
* 🔄 CMS / Airtable syncing via webhook
* 📊 Admin dashboard (top queries, usage)
* 🎭 Multi-event switching with MCP profiles

---

## ✅ Success Criteria

* Functional tablet UI
* RAG responses based on uploaded content
* Secure admin dashboard
* Response time < 3s

## 🗓️ Sprint Timeline

**Week 1**: UI Shell, MCP Setup, Sample Data **Week 2**: RAG + Integration, Admin Panel, Testing

## 🌟 Contributors

* Product Owner: Matthew Wallace
* Engineering: Banyan Labs MCP + FE Team
* Customer: Vant4ge

## 🚀 Run the Project Locally

```bash
# Frontend
cd mcp-rag-demo
npm install
npm start

# Backend
cd backend
uvicorn main:app --reload
```

> 📅 This README.md captures the full project scope and gives step-by-step developer instructions. Ensure all credentials and environment variables are securely managed.












🎯 Project Vision
As a conference attendee, I want to interact with AIDA through an intuitive tablet interface so that I can learn about the conference, demo capabilities, and product features in an engaging conversational experience.

🏗 Architecture Overview
Frontend
- React app optimized for iPad/Android tablets
- Component Library: AG UI
- Hosting: Vercel
- Auth: Clerk (admin/preview access)
Backend (MCP Layer)
- Framework: FastAPI + Docker
- MCP Core: Armada’s MCP framework
- RAG Knowledge Base:
- Conference schedule & logistics
- AIDA demo details
- Scripted conversation flows
- Vector Store: Supabase (Postgres + pgvector or Edge Functions)
- Logging & Analytics: Basic interaction tracking

🌟 Core Features (MVP)
1. AI Chat Interface
- Conversational UI powered by GPT-4o or Claude 3
- Text-based interaction with optional scripted responses
- Answers include:
- Event schedule, locations, sessions
- AIDA feature info & technical background
- FAQs curated by Vant4ge
2. MCP-Driven RAG Backend
- Ingest conference metadata (JSON/CSV/Airtable)
- Tooling support defined via MCP schema
- Logging + basic analytics
3. Basic Admin Interface
- Secure file upload (JSON/CSV) for conference data
- Clerk-protected access for Vant4ge/Banyan teams

🔧 Tech Stack
| Layer | Technology | 
| Frontend | React + AG UI | 
| Hosting | Vercel | 
| Auth | Clerk | 
| Backend (MCP) | FastAPI + Armada MCP Core | 
| Database | Supabase (Postgres + pgvector) | 
| AI Model | GPT-4o / Claude 3 (via API) | 
| Containerization | Docker | 
| Testing | Pytest + FastAPI TestClient | 



🚀 Getting Started
Prerequisites
- Node.js ≥ 18
- Python ≥ 3.10
- Docker & Docker Compose
- Git
Environment Variables
Create a .env in the root (backend) and .env.local in frontend/:
# backend/.env
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
# any other MCP/Armada settings

# frontend/.env.local
NEXT_PUBLIC_SUPABASE_URL=https://xyz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...


Clone & Install
# Clone repo
git clone https://github.com/SNoeCode/mcp-rag-demo.git
cd mcp-rag-demo

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..


Running the Backend
docker build -t mcp-rag-backend .
docker run -p 8000:8000 --env-file .env mcp-rag-backend


- Health Check: GET http://localhost:8000/health
- MCP Health:   GET http://localhost:8000/mcp/health-mcp
Running the Frontend
cd frontend
npm run dev


- Open your tablet-simulated browser at: http://localhost:3000
Running Tests
# Run FastAPI backend tests
pytest --maxfail=1 --disable-warnings -q

# Run any React frontend tests (if added)
cd frontend && npm test



🔀 Branching Strategy
- main → Production-ready, updated only when merging develop.
- develop → Integration branch for all new work.
- feature/* → New features branch off develop.
- bugfix/* → Bug fixes branch off develop.
- hotfix/* → Urgent fixes branch off develop.
- release/* → (Optional) Version branches off develop for QA before merging into main.

📅 Sprint 1 Deliverables & Timeline
| Week | Days | Goals / Tasks | 
| 1 | Days 1–2 | Setup FastAPI, Docker, Supabase connection | 
|  | Days 3–4 | Scaffold React + AG UI chat interface with dummy messaging | 
|  | Day 5 | Implement MCP endpoint (basic schema) + health check | 
| 2 | Days 1–2 | Load sample conference/AIDA data into Supabase; build RAG retrieval logic | 
|  | Days 3–4 | Connect frontend → backend; run integration tests | 
|  | Day 5 | Build basic admin interface; finalize testing; prepare for sprint review | 



🔥 Epic & User Stories
Epic 1: Core Chat Experience
- Story 1.1: Basic tablet-optimized chat UI
- Story 1.2: Message flow & dummy responses
Epic 2: RAG-Powered Knowledge System
- Story 2.1: MCP Backend foundation
- Story 2.2: RAG integration with Supabase
- Story 2.3: Sample data ingestion
Epic 3: Admin Content Management
- Story 3.1: Secure admin interface for data uploads
Epic 4: Technical Foundation
- Story 4.1: Vercel hosting & deployment pipeline
- Story 4.2: Supabase vector storage setup

🌍 Future Roadmap (Post-MVP)
- Voice chat integration (Whisper / streaming)
- Multi-session management & engagement tracking
- Live data updates via CMS/Airtable webhooks
- Analytics dashboard (top queries, usage trends)
- Multiple conference profiles via MCP “profiles”

🤝 Contributing
- Fork the repo & clone locally
- Create a branch off develop (e.g. feature/awesome-thing)
- Make your changes & write tests
- Push & open a PR → develop
- After review, merge & delete your branch

📜 License
MIT © SNoeCode
Feel free to adapt and extend this demo for your own RAG + MCP experiments!

This file is **ready to save as `README.md`** and commit to your repo. 🚀 Let me know if you'd like any modifications!


 -->













# MCP-RAG-Demo
🎯 Project Overview

We are building a tablet-optimized React application for Vant4ge to demo AIDA, our AI assistant, at an upcoming conference. The goal is to provide a scripted and intelligent experience where attendees can interact with AIDA and ask questions about the conference, the demo, and the product experience.

The backend will be powered by Armada, our MCP layer, using Retrieval-Augmented Generation (RAG) to feed the AI with curated data and context. The front end will use AG UI components for a clean and scalable experience and rely on Supabase, Clerk, and Vercel for backend, auth, and hosting infrastructure.

🧱 Architecture Overview

🔹 Frontend
React App (optimized for iPad/Android tablets)
Component library: AG UI
Hosted on Vercel
Auth via Clerk (for admin/secure preview access)

🔹 Backend (MCP Layer)
Built on top of Armada's MCP framework
RAG-powered knowledge base fed by:
Conference schedule & logistics
AIDA demo experience details (provided by Vant4ge)
Scripted conversation flow guidance
Vector database: Supabase Edge Functions or integrated Postgres/Vector store
Guardrails & endpoint tooling defined via MCP concepts

📲 Core Features (MVP Scope)

1. AI Chat Interface
Conversational UI powered by GPT (e.g., GPT-4o or Claude 3, pending eval)
Text-based interaction with optional scripted responses
Capable of answering:
Event schedule, locations, sessions
AIDA feature info & technical background
FAQs curated by Vant4ge

2. MCP-Driven RAG Backend
Conference metadata ingested via structured formats (JSON, CSV, Airtable, etc.)
Tooling support (functions, external links) defined in MCP schema
Logging + basic analytics of interactions

3. Basic Admin Interface
Upload static data to MCP (Vant4ge content team)
Auth via Clerk for internal use only (Vant4ge/Banyan teams)

🧪 Sprint 1 Deliverables (Weeks 1–2)



Area
Deliverable
🧱 Frontend
Basic UI shell with AG UI layout
💬 Chat UI
Working chat input/output flow (dummy LLM or placeholder initially)
🧠 Backend
Initial MCP endpoint with basic schema for conference info
📚 RAG Setup
Upload sample conference + AIDA data provided by Vant4ge
🔁 RAG Integration
Connect frontend to backend for RAG-augmented answers
🧪 QA
Internal testing flow: Ask AIDA about key conference info

🔄 Tech Stack



Layer
Tooling
Hosting
Vercel
Auth
Supabase for POC → Clerk for Production
DB / Vector Store
Supabase (Postgres w/ pgvector or embeddings)
Frontend
React + AG UI
AI Model
GPT-4o or Claude 3 via API
Backend (MCP)
Armada MCP Core + RAG Endpoints

🧭 Future Iterations (Post-MVP)

Voice chat integration (whisper / streaming)
Multi-session management (track engagement)
Live data updates (webhooks from CMS or Airtable)
Analytics dashboard (usage trends, top queries)
Multiple conference support via MCP “profiles”

👥 Key Stakeholders



Role
Name
Product Owner
Matthew Wallace (Banyan Labs)
Partner / Customer
Vant4ge Product & Marketing Team
AI Experience Lead
[Insert Vant4ge Contact]
Engineering
Banyan Labs MCP + Frontend Teams

✅ Success Criteria (for MVP)

Working tablet-ready UI with stable, styled chat interface
RAG system returns accurate answers from uploaded Vant4ge data
Vant4ge team can simulate AIDA conference experience end-to-end
Positive internal feedback on usability and experience flow

🗓️ Target Sprint 1 Timeline

Kickoff: [Insert Date]
Sprint Review: [Insert Date 2 weeks later]
Data Handoff from Vant4ge: Within 3 days of kickoff
LLM Model Selection Finalized: Within 1 week

Let me know if you’d like a Notion version of this brief or a ClickUp project plan generated from it.




🎯 Project Vision
As a conference attendee, I want to interact with AIDA through an intuitive tablet interface so that I can learn about the conference, demo capabilities, and product features in an engaging conversational experience.


📋 Epic Breakdown
Epic 1: Core Chat Experience
Goal: Deliver a functional chat interface that conference attendees can use to interact with AIDA
Epic 2: RAG-Powered Knowledge System
Goal: Implement intelligent responses using conference and product data
Epic 3: Admin Content Management
Goal: Enable Vant4ge team to manage and upload demo content
Epic 4: Technical Foundation
Goal: Establish robust, scalable technical infrastructure


🏃‍♂️ Sprint 1 User Stories
Epic 1: Core Chat Experience
Story 1.1: Basic Chat Interface
As a conference attendee
I want to see a clean, tablet-optimized chat interface
So that I can easily interact with AIDA on an iPad or Android tablet
Acceptance Criteria:
[ ] Chat interface displays properly on tablet screens (10-13 inches)
[ ] Input field is easily accessible and responsive to touch
[ ] Message history scrolls smoothly
[ ] Uses reusable UI components for consistent styling
[ ] Interface is intuitive without training
Story Points: 5
Tasks:
[ ] Set up React project 
[ ] Research reusable component libraries
[ ] Create responsive chat container component
[ ] Implement message input component with touch optimization
[ ] Design message bubble components or use one from library
[ ] Add scroll behavior for message history
[ ] Test on multiple tablet screen sizes
[ ] Implement basic loading states


Story 1.2: Message Flow
As a conference attendee
I want to send messages and receive responses from AIDA
So that I can have a natural conversation experience
Acceptance Criteria:
[ ] User can type and send messages
[ ] Mock data is used to test 
[ ] Messages appear in chat history immediately
[ ] AI responses display with appropriate timing/animation
[ ] Messages are clearly distinguished between user and AI
[ ] Character limits are handled gracefully
Story Points: 3
Tasks:
[ ] Implement message state management
[ ] Create send message functionality
[ ] Use mock message data for testing
[ ] Add message timestamp handling
[ ] Implement typing indicators
[ ] Add message delivery confirmation
[ ] Handle empty/invalid message submission


Epic 2: RAG-Powered Knowledge System
Story 2.1: MCP Backend Foundation
As a system administrator
I want a working MCP endpoint that can process conference data
So that AIDA can provide intelligent responses about the event
Acceptance Criteria:
[ ] MCP endpoint accepts and processes conference data
[ ] Basic schema defined for conference information
[ ] Endpoint returns structured responses
[ ] Error handling for malformed requests
[ ] Basic logging implemented
Story Points: 8
Tasks:
[ ] Set up Armada MCP core infrastructure or adjust existing core accordingly
[ ] Define conference data schema (JSON/CSV structure)
[ ] Create basic MCP endpoint for data ingestion
[ ] Implement error handling and validation
[ ] Set up basic logging system
[ ] Create health check endpoint
[ ] Document API endpoints


Story 2.2: RAG Integration
As a conference attendee
I want AIDA to answer questions using real conference data
So that I get accurate, relevant information about the event
Acceptance Criteria:
[ ] Frontend connects to MCP backend successfully
[ ] RAG system retrieves relevant information for queries
[ ] Responses include conference-specific details
[ ] System handles "I don't know" scenarios gracefully
[ ] Response time is under 3 seconds for typical queries
Story Points: 13
Tasks:
[ ] Set up Supabase vector database
[ ] Implement RAG retrieval logic
[ ] Connect frontend to backend API
[ ] Add query processing and context building
[ ] Implement fallback responses for unknown topics
[ ] Add response caching for common queries
[ ] Test with sample conference data


Story 2.3: Sample Data Integration
As a Vant4ge team member
I want sample conference and AIDA data loaded into the system
So that we can test the complete user experience
Acceptance Criteria:
[ ] Sample conference schedule uploaded successfully
[ ] AIDA product information available in knowledge base
[ ] FAQ data integrated and searchable
[ ] Data covers key demo scenarios
[ ] System responds accurately to test queries
Story Points: 5
Tasks:
[ ] Create sample conference data (schedule, sessions, locations)
[ ] Prepare AIDA product information dataset
[ ] Create FAQ dataset for common questions
[ ] Upload data to vector database
[ ] Test data retrieval accuracy
[ ] Validate responses match expected content


Epic 3: Admin Content Management
Story 3.1: Basic Admin Interface
As a Vant4ge content manager
I want a simple interface to upload conference data
So that I can manage the content AIDA will reference
Acceptance Criteria:
[ ] Secure admin interface accessible via authentication
[ ] File upload functionality for JSON/CSV data
[ ] Upload progress indication
[ ] Success/error feedback for uploads
[ ] Basic data validation before processing
Story Points: 8
Tasks:
[ ] Set up Clerk/Supabase authentication
[ ] Create admin dashboard layout
[ ] Implement file upload component
[ ] Add data validation logic
[ ] Create upload progress tracking
[ ] Implement success/error notifications
[ ] Add basic user role management


Epic 4: Technical Foundation
Story 4.1: Hosting and Deployment
As a developer
I want the application deployed to Vercel with proper configuration
So that the demo is accessible and performant for conference use
Acceptance Criteria:
[ ] Application successfully deployed to Vercel
[ ] Environment variables properly configured
[ ] Build process optimized for production
[ ] HTTPS and security headers configured
[ ] Performance meets tablet optimization standards
Story Points: 3
Tasks:
[ ] Configure Vercel deployment pipeline
[ ] Set up environment variables
[ ] Optimize build configuration
[ ] Configure security headers
[ ] Set up monitoring and error tracking
[ ] Test deployment on tablet devices


Story 4.2: Database Setup
As a system administrator
I want Supabase configured with vector storage capabilities
So that the RAG system can efficiently store and retrieve data
Acceptance Criteria:
[ ] Supabase project created and configured
[ ] Vector storage (pgvector) enabled
[ ] Database schema matches MCP requirements
[ ] Connection pooling configured for performance
[ ] Backup and recovery procedures documented
Story Points: 5
Tasks:
[ ] Create Supabase project
[ ] Enable pgvector extension
[ ] Design database schema for conference data
[ ] Set up connection configuration
[ ] Configure database security rules
[ ] Test database performance with sample data


🧪 Definition of Done
For each User Story:
[ ] All acceptance criteria met
[ ] Code reviewed and approved
[ ] Unit tests written and passing
[ ] Integration tested on tablet devices
[ ] Documented for handoff
[ ] Performance validated (under 3s response time)
[ ] Accessibility requirements met
[ ] Security review completed
For Sprint 1:
[ ] All user stories completed
[ ] End-to-end demo flow working
[ ] Vant4ge team can test complete experience
[ ] Performance benchmarks met
[ ] Deployment to staging environment successful


🎯 Sprint 1 Capacity Planning
Total Story Points: 50 Sprint Duration: 2 weeks Team Velocity Estimate: 25-30 points per week
Priority Order:
Story 4.1 & 4.2 (Technical Foundation) - 8 points
Story 1.1 & 1.2 (Basic Chat) - 8 points
Story 2.1 (MCP Backend) - 8 points
Story 2.3 (Sample Data) - 5 points
Story 2.2 (RAG Integration) - 13 points
Story 3.1 (Admin Interface) - 8 points


🚀 Success Metrics
Technical Metrics:
Response time < 3 seconds for 95% of queries
Zero critical security vulnerabilities
99% uptime during demo period
Mobile/tablet performance score > 90
User Experience Metrics:
Successful end-to-end demo completion
Positive feedback from Vant4ge team
All key conference scenarios testable
Intuitive user interaction (no training required)


📅 Sprint 1 Timeline
Week 1:
Days 1-2: Technical foundation setup
Days 3-4: Basic chat interface development
Day 5: MCP backend foundation
Week 2:
Days 1-2: Sample data integration and RAG setup
Days 3-4: RAG integration and testing
Day 5: Admin interface and final testing


  
