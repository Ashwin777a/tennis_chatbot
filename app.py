import streamlit as st
import requests
import os

# -----------------------------
# Configuration
# -----------------------------
API_URL = os.getenv("API_URL", "http://localhost:8000")

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="CE Tennis Academy Bot",
    page_icon="🎾",
    layout="centered"
)

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown("""
    <div class="main-header">
        <h1>🎾 CE Tennis Academy Assistant</h1>
        <p>Ask me anything about our academy!</p>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("ℹ️ About")
    st.write("This chatbot helps you learn about CE Tennis Academy's programs, facilities, and schedules.")
    
    st.header("⚙️ Settings")
    n_results = st.slider("Number of context sources", 1, 10, 3)
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        try:
            requests.post(f"{API_URL}/clear-memory")
        except:
            pass
        st.rerun()
    
    st.divider()
    
    # Health check
    try:
        health = requests.get(f"{API_URL}/health", timeout=2).json()
        if health.get("status") == "healthy":
            st.success("✅ API Connected")
            st.caption(f"📊 {health.get('documents_in_db', 0)} documents indexed")
        else:
            st.error("❌ API Unhealthy")
    except:
        st.error("❌ Cannot connect to API")
        st.caption(f"Trying to connect to: {API_URL}")

# -----------------------------
# Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# Display Chat History
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -----------------------------
# Chat Input
# -----------------------------
user_input = st.chat_input("Ask about programs, facilities, coaches, timings...")

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.write(user_input)
    
    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"query": user_input, "n_results": n_results},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    sources = data.get("sources_found", 0)
                    
                    st.write(answer)
                    
                    # Show metadata
                    if sources > 0:
                        st.caption(f"📚 Answer based on {sources} source(s)")
                else:
                    st.error(f"API Error: {response.status_code}")
                    answer = "Sorry, I encountered an error. Please try again."
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Is it running?")
                answer = "Connection error. Please check if the API is running."
            
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out")
                answer = "The request took too long. Please try again."
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
                answer = "An unexpected error occurred."
    
    # Store assistant response
    st.session_state.messages.append({"role": "assistant", "content": answer})

# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption("Powered by ChromaDB, Groq LLM & Streamlit | CE Tennis Academy")