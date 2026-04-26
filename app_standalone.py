"""
Standalone Tennis Academy Chatbot
Combines FastAPI logic into Streamlit for easier deployment
Perfect for Streamlit Cloud hosting (100% free!)
"""

import streamlit as st
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
from collections import deque
import os

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="CE Tennis Academy Bot",
    page_icon="🎾",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .info-box {
        background: #f0f9ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------
# Initialize Components (Cached)
# -----------------------------
@st.cache_resource
def load_model():
    """Load embedding model (cached)"""
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def load_chromadb():
    """Load ChromaDB client and collection (cached)"""
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="tennis_data")
    return client, collection

@st.cache_resource
def load_groq():
    """Load Groq client (cached)"""
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found! Add it to Streamlit secrets or environment variables.")
        return None
    return Groq(api_key=api_key)

# Load components
model = load_model()
client, collection = load_chromadb()
groq_client = load_groq()

# -----------------------------
# Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = deque(maxlen=5)

# -----------------------------
# Helper Functions
# -----------------------------
def retrieve_context(query: str, n_results: int = 3):
    """Retrieve relevant context from ChromaDB"""
    try:
        query_embedding = model.encode([query]).tolist()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        docs = results.get("documents", [[]])[0]
        return " ".join(docs), len(docs)
    except Exception as e:
        st.error(f"Error retrieving context: {e}")
        return "", 0

def generate_response(user_query: str, n_results: int = 3):
    """Generate response using RAG"""
    if not groq_client:
        return "Groq API not configured. Please add GROQ_API_KEY.", 0
    
    # Retrieve context
    context, sources_count = retrieve_context(user_query, n_results)
    
    # Build memory context
    memory_context = "\n".join(
        [f"User: {m['user']}\nAssistant: {m['assistant']}" 
         for m in st.session_state.memory]
    )
    
    # Build prompt
    prompt = f"""You are a helpful assistant for CE Tennis Academy in Chennai.

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
- Focus on programs, facilities, coaches, timings, and fees

Answer:"""
    
    try:
        # Call Groq
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Store in memory
        st.session_state.memory.append({
            "user": user_query,
            "assistant": answer
        })
        
        return answer, sources_count
    
    except Exception as e:
        return f"Error generating response: {str(e)}", 0

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("ℹ️ About")
    st.write("This AI chatbot helps you learn about CE Tennis Academy's programs, facilities, and schedules.")
    
    st.divider()
    
    st.header("⚙️ Settings")
    n_results = st.slider("Context sources", 1, 10, 3, 
                          help="Number of relevant chunks to retrieve")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.memory.clear()
        st.rerun()
    
    st.divider()
    
    # Database info
    try:
        doc_count = collection.count()
        st.success("✅ Database Connected")
        st.caption(f"📊 {doc_count} chunks indexed")
    except:
        st.error("❌ Database not found")
        st.caption("Run scraping script first")
    
    # API status
    if groq_client:
        st.success("✅ Groq API Ready")
    else:
        st.error("❌ Groq API Missing")
    
    st.divider()
    
    # Sample questions
    st.header("💡 Sample Questions")
    sample_questions = [
        "What programs do you offer?",
        "What are your timings?",
        "Tell me about the coaches",
        "What facilities are available?",
        "How much does it cost?"
    ]
    
    for question in sample_questions:
        if st.button(question, key=question, use_container_width=True):
            # Add to chat
            st.session_state.messages.append({
                "role": "user",
                "content": question
            })
            st.rerun()

# -----------------------------
# Main Header
# -----------------------------
st.markdown("""
    <div class="main-header">
        <h1>🎾 CE Tennis Academy Assistant</h1>
        <p style='margin: 0; opacity: 0.9;'>Ask me anything about our academy!</p>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Display Chat History
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "sources" in msg and msg["sources"] > 0:
            st.caption(f"📚 Based on {msg['sources']} source(s)")

# -----------------------------
# Chat Input
# -----------------------------
user_input = st.chat_input("Ask about programs, facilities, coaches, timings...")

if user_input:
    # Display user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    with st.chat_message("user"):
        st.write(user_input)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, sources = generate_response(user_input, n_results)
            st.write(answer)
            
            if sources > 0:
                st.caption(f"📚 Based on {sources} source(s)")
    
    # Store assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })
    
    # Auto-scroll (rerun to show new messages)
    st.rerun()

# -----------------------------
# Footer
# -----------------------------
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🤖 Powered by AI")
