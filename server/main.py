from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

import openai
from services.rag_service import RAGService
from services.supabase_service import SupabaseService

app = FastAPI(title="AIDA Conference Assistant API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
supabase_service = SupabaseService()
rag_service = RAGService()

class ChatRequest(BaseModel):
    message: str
from typing import List, Any

class ChatResponse(BaseModel):
    response: str
    sources: List[Any] = []
    sources: list = []

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Get relevant context from RAG
        context = await rag_service.get_relevant_context(request.message)
        
        # Generate response using OpenAI
        response = await rag_service.generate_response(request.message, context)
        
        # Log conversation to Supabase
        await supabase_service.log_conversation(request.message, response)
        
        return ChatResponse(response=response, sources=context.get('sources', []))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
