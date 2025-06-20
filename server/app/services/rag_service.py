import openai
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from typing import Dict, List
import os

class RAGService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection("conference_data")
        
        # Load sample data
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample conference data into vector store"""
        sample_data = [
            {
                "content": "The Vant4ge Tech Conference runs from June 15-17, 2025 at the Austin Convention Center.",
                "metadata": {"type": "schedule", "topic": "dates"}
            },
            {
                "content": "AIDA is an AI-powered assistant that helps with data analysis, customer service, and workflow automation.",
                "metadata": {"type": "product", "topic": "aida_features"}
            },
            {
                "content": "The main keynote is on June 16 at 9:00 AM featuring the future of AI in business.",
                "metadata": {"type": "schedule", "topic": "keynote"}
            },
            {
                "content": "Lunch is served daily from 12:00-1:30 PM in the main exhibition hall.",
                "metadata": {"type": "logistics", "topic": "food"}
            },
            {
                "content": "AIDA can integrate with over 100+ popular business tools including Salesforce, HubSpot, and Slack.",
                "metadata": {"type": "product", "topic": "integrations"}
            }
        ]
        
        # Check if data already loaded
        if self.collection.count() == 0:
            for i, item in enumerate(sample_data):
                embedding = self.embedding_model.encode(item["content"]).tolist()
                self.collection.add(
                    embeddings=[embedding],
                    documents=[item["content"]],
                    metadatas=[item["metadata"]],
                    ids=[f"doc_{i}"]
                )
    
    async def get_relevant_context(self, query: str, top_k: int = 3) -> Dict:
        """Retrieve relevant context for a query using RAG"""
        # Generate embedding for query
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search for similar documents
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        context = {
            "documents": results["documents"][0] if results["documents"] else [],
            "sources": results["metadatas"][0] if results["metadatas"] else []
        }
        
        return context
    
    async def generate_response(self, query: str, context: Dict) -> str:
        """Generate response using OpenAI with RAG context"""
        # Build context string
        context_str = "\n".join(context["documents"]) if context["documents"] else ""
        
        # Create prompt
        prompt = f"""You are AIDA, a helpful AI assistant for the Vant4ge Tech Conference. 
Use the following context to answer the user's question. If the context doesn't contain 
relevant information, provide a helpful general response about being a conference assistant.


Context:
{context_str}

User Question: {query}

Response:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are AIDA, a friendly and helpful conference assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Please try again later."
