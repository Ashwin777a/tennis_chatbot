from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
from collections import deque
from groq import Groq
import os
from typing import Optional

# -----------------------------
# Init App
# -----------------------------
app = FastAPI(title="Tennis Academy Chatbot API")

# -----------------------------
# Load Embedding Model
# -----------------------------
print("🔄 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# ChromaDB (Persistent)
# -----------------------------
print("🔄 Connecting to ChromaDB...")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="tennis_data")

# -----------------------------
# Groq LLM
# -----------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("⚠️  WARNING: GROQ_API_KEY environment variable not set!")
    print("Set it using: export GROQ_API_KEY='your-key-here'")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# -----------------------------
# Memory (last 5 conversations)
# -----------------------------
memory = deque(maxlen=5)

# -----------------------------
# Request Schema
# -----------------------------
class QueryRequest(BaseModel):
    query: str
    n_results: Optional[int] = 3


class ChatResponse(BaseModel):
    answer: str
    memory_size: int
    sources_found: int


# -----------------------------
# Retrieve Context
# -----------------------------
def retrieve_context(query: str, n_results: int = 3) -> tuple[str, int]:
    """
    Retrieve relevant context from ChromaDB
    Returns: (context_string, number_of_sources)
    """
    try:
        query_embedding = model.encode([query]).tolist()
        
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        docs = results.get("documents", [[]])[0]
        return " ".join(docs), len(docs)
    
    except Exception as e:
        print(f"❌ Error retrieving context: {e}")
        return "", 0


# -----------------------------
# Chat Endpoint
# -----------------------------
@app.post("/chat", response_model=ChatResponse)
def chat(req: QueryRequest):
    """
    Main chat endpoint for tennis academy queries
    """
    if not groq_client:
        raise HTTPException(
            status_code=500,
            detail="Groq API key not configured. Please set GROQ_API_KEY environment variable."
        )
    
    user_query = req.query.strip()
    
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # 1. Retrieve context
    context, sources_count = retrieve_context(user_query, req.n_results)
    
    # 2. Build memory context
    memory_context = "\n".join(
        [f"User: {m['user']}\nAssistant: {m['assistant']}" for m in memory]
    )
    
    # 3. Build prompt
    prompt = f"""You are a helpful assistant for CE Tennis Academy (Chennai).

Previous conversation:
{memory_context if memory_context else "None"}

Context from academy website:
{context if context else "No relevant information found"}

User question:
{user_query}

Instructions:
- Be friendly and professional
- Use the context to provide accurate information about the academy
- If the information is not in the context, politely say you don't have that specific information
- Keep answers concise and relevant
- If asked about facilities, programs, coaches, or timings, refer to the context

Answer:"""

    try:
        # 4. Call Groq LLM
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Better model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
    
    # 5. Store in memory
    memory.append({
        "user": user_query,
        "assistant": answer
    })
    
    return ChatResponse(
        answer=answer,
        memory_size=len(memory),
        sources_found=sources_count
    )


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health_check():
    """Check if API is running and ChromaDB is accessible"""
    try:
        count = collection.count()
        return {
            "status": "healthy",
            "documents_in_db": count,
            "groq_configured": groq_client is not None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# -----------------------------
# Clear Memory Endpoint
# -----------------------------
@app.post("/clear-memory")
def clear_memory():
    """Clear conversation memory"""
    memory.clear()
    return {"message": "Memory cleared successfully"}


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)