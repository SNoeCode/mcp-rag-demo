from supabase import create_client, Client
import os
from datetime import datetime

class SupabaseService:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Create table if it doesn't exist
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure required tables exist in Supabase"""
        # This would typically be done via Supabase migrations
        # For now, we'll handle it programmatically
        pass
    
    async def log_conversation(self, user_message: str, ai_response: str):
        """Log conversation to Supabase"""
        try:
            data = {
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": "demo_session"  # For now, use a fixed session
            }
            
            result = self.supabase.table("conversations").insert(data).execute()
            return result
        
        except Exception as e:
            print(f"Error logging conversation: {e}")
            return None
    
    async def get_conversation_history(self, session_id: str = "demo_session"):
        """Get conversation history"""
        try:
            result = self.supabase.table("conversations")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("timestamp", desc=False)\
                .execute()
            
            return result.data
        
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
