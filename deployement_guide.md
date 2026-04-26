# Free Hosting Options for Your Tennis Academy Chatbot

## 🎯 Recommended Free Hosting Solutions

### Option 1: **Render.com** (Best for beginners) ⭐ RECOMMENDED

**Pros:**
- Completely free tier
- Easy deployment from GitHub
- Automatic HTTPS
- Both FastAPI and Streamlit can be hosted
- 750 hours/month free (enough for 24/7 uptime)

**Limitations:**
- Spins down after 15 minutes of inactivity (cold starts)
- 512 MB RAM on free tier

**Steps:**
1. Push your code to GitHub
2. Sign up at render.com
3. Create two Web Services:
   - **Backend (FastAPI)**: 
     - Build command: `pip install -r requirements.txt`
     - Start command: `python main.py`
     - Add environment variable: `GROQ_API_KEY`
   - **Frontend (Streamlit)**: 
     - Build command: `pip install -r requirements.txt`
     - Start command: `streamlit run app.py --server.port $PORT`
     - Add environment variable: `API_URL=https://your-backend-url.onrender.com`

---

### Option 2: **Railway.app** (Good alternative)

**Pros:**
- $5 free credit monthly (enough for small apps)
- No sleep/cold starts
- Easier configuration

**Limitations:**
- Free credit runs out if you use too much

**Steps:**
1. Sign up at railway.app
2. Deploy from GitHub repo
3. Configure start commands and environment variables

---

### Option 3: **Hugging Face Spaces** (For Streamlit only)

**Pros:**
- Unlimited hosting for ML apps
- Great for demos
- Built-in GPU support (for larger models)

**Limitations:**
- Need to combine backend and frontend in one app
- Less flexibility

**Steps:**
1. Create a Space at huggingface.co/spaces
2. Choose "Streamlit" SDK
3. Upload your code
4. Integrate FastAPI within Streamlit or use Gradio instead

---

### Option 4: **Fly.io** (Advanced)

**Pros:**
- Free tier with 3 shared VMs
- Better performance
- More control

**Limitations:**
- Requires Docker knowledge
- More complex setup

---

## 📦 Database Storage Solutions

### **ChromaDB Storage:**
Since ChromaDB creates a local directory (`./chroma_db`), you need persistent storage:

1. **Render.com**: Use persistent disk (free 1GB)
2. **Railway.app**: Automatic volume mounting
3. **Alternative**: Host ChromaDB data on **Supabase** or **PlanetScale** (requires code changes)

---

## 🚀 Quick Deployment Guide (Render.com)

### Step 1: Prepare Your Code

```bash
# Create a GitHub repository
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/tennis-chatbot.git
git push -u origin main
```

### Step 2: Create Render.com Services

**Backend Service (FastAPI):**
```yaml
# render.yaml (create this file)
services:
  - type: web
    name: tennis-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python main.py"
    envVars:
      - key: GROQ_API_KEY
        sync: false
    disk:
      name: chroma-data
      mountPath: /home/claude/chroma_db
      sizeGB: 1
```

**Frontend Service (Streamlit):**
```yaml
  - type: web
    name: tennis-chatbot
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"
    envVars:
      - key: API_URL
        value: https://tennis-api.onrender.com
```

### Step 3: Initial Data Scraping

Since scraping creates the database, you need to run it once:

**Option A**: Run locally, then upload `chroma_db` folder
**Option B**: Create a one-time job on Render to run `scraping_and_embedding.py`

---

## 💡 Alternative: All-in-One Deployment

Combine everything into a single Streamlit app:

```python
# Create a new file: streamlit_standalone.py
import streamlit as st
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

# Initialize once
@st.cache_resource
def load_components():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="tennis_data")
    groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
    return model, collection, groq

# ... rest of your logic here
```

Then deploy only this file to **Streamlit Cloud** (totally free):
- Go to streamlit.io/cloud
- Connect GitHub repo
- Add `GROQ_API_KEY` to secrets
- Deploy!

---

## 📊 Cost Comparison

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| Render.com | 750 hrs/month | Separate backend/frontend |
| Railway.app | $5/month credit | No cold starts |
| Streamlit Cloud | Unlimited | All-in-one apps |
| Hugging Face | Unlimited | ML demos |
| Fly.io | 3 VMs | Advanced users |

---

## ⚡ Performance Tips

1. **Reduce model size**: Use `all-MiniLM-L6-v2` (already set)
2. **Limit chunk storage**: Only embed important pages
3. **Cache embeddings**: Done with ChromaDB
4. **Use async FastAPI**: For better concurrency
5. **Compress ChromaDB**: Enable compression in settings

---

## 🔧 Troubleshooting

**Cold Start Issues (Render):**
- Keep app alive with UptimeRobot (free monitoring)
- Ping your API every 14 minutes

**Memory Issues:**
- Reduce `n_results` in queries
- Use smaller embedding model
- Clear old data from ChromaDB

**Slow Response:**
- Use faster Groq models
- Reduce context size
- Implement caching

---

## 🎁 My Recommendation for You

**Use Streamlit Cloud** with the all-in-one approach:
1. Combine FastAPI logic into Streamlit
2. Upload pre-scraped `chroma_db` to GitHub (if < 100MB)
3. Deploy to Streamlit Cloud
4. Zero cost, zero maintenance!

If you need separate services: **Render.com**