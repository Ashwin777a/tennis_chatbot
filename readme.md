# 🎾 CE Tennis Academy Chatbot

An AI-powered chatbot for CE Tennis Academy that answers questions about programs, facilities, coaches, and schedules using RAG (Retrieval-Augmented Generation).

## 🏗️ Architecture

```
Web Scraping → Chunking → Embeddings → ChromaDB (Vector Store)
                                              ↓
User Query → Embedding → Similarity Search → Context Retrieval
                                              ↓
                              Context + Query → Groq LLM → Answer
```

## ✨ Key Improvements from Original Code

✅ **No intermediate text files** - Direct scraping to vector DB  
✅ **Environment variables** - Secure API key management  
✅ **Better error handling** - Robust request handling  
✅ **Health checks** - API monitoring endpoint  
✅ **Improved UI** - Professional Streamlit interface  
✅ **Memory management** - Conversation context tracking  
✅ **Source attribution** - Shows number of sources used  

## 📁 Project Structure

```
.
├── scraping_and_embedding.py  # Scrape website & populate ChromaDB
├── main.py                     # FastAPI backend
├── app.py                      # Streamlit frontend
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── DEPLOYMENT_GUIDE.md        # Hosting instructions
└── chroma_db/                 # Vector database (created after scraping)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Groq API key
# Get one free at: https://console.groq.com
```

### 3. Scrape and Embed Data

```bash
python scraping_and_embedding.py
```

This will:
- Scrape all HTML pages from cetennis.in
- Extract and clean text content
- Create embeddings
- Store directly in ChromaDB (no text files!)

### 4. Run the Backend API

```bash
# Set your API key (or use .env file)
export GROQ_API_KEY='your-key-here'

# Start the API
python main.py
```

API will run at: http://localhost:8000

### 5. Run the Frontend

```bash
# In a new terminal
streamlit run app.py
```

Chatbot will open at: http://localhost:8501

## 🧪 Test the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Chat Query
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What programs do you offer?"}'
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check API status & DB count |
| `/chat` | POST | Send a query and get response |
| `/clear-memory` | POST | Clear conversation history |

## 🔧 Configuration

### Scraping Settings
Edit in `scraping_and_embedding.py`:
```python
BASE_URL = "https://cetennis.in/"
CHUNK_SIZE = 300        # Words per chunk
CHUNK_OVERLAP = 50      # Overlap between chunks
```

### Retrieval Settings
Edit in `main.py`:
```python
n_results = 3           # Number of context chunks to retrieve
```

### LLM Settings
Edit in `main.py`:
```python
model="llama-3.3-70b-versatile"  # Groq model
temperature=0.7                    # Response creativity
max_tokens=500                     # Response length
```

## 🆓 Free Hosting Options

See **DEPLOYMENT_GUIDE.md** for detailed instructions on:

1. **Render.com** (Recommended) - Free tier with persistent storage
2. **Streamlit Cloud** - Perfect for all-in-one deployment
3. **Railway.app** - $5/month free credit
4. **Hugging Face Spaces** - Unlimited for ML apps

## 🐛 Troubleshooting

### "Groq API key not configured"
```bash
# Make sure environment variable is set
export GROQ_API_KEY='your-actual-key'

# Or create a .env file with:
GROQ_API_KEY=your-actual-key
```

### "Cannot connect to API"
- Check if main.py is running
- Verify API_URL in app.py matches your backend URL
- Check firewall/port settings

### "No documents found"
- Run `scraping_and_embedding.py` first
- Check if `chroma_db` folder exists
- Verify ChromaDB has data: check `/health` endpoint

### Cold Start Issues (Deployed)
- Use UptimeRobot to ping your app every 14 minutes
- Consider upgrading to paid tier for no-sleep hosting

## 📝 Example Queries

Try asking:
- "What tennis programs do you offer?"
- "What are your timings?"
- "Tell me about the coaching staff"
- "What facilities do you have?"
- "How much does it cost?"

## 🔐 Security Notes

⚠️ **Never commit your .env file to GitHub!**

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "chroma_db/" >> .gitignore
```

## 🎯 Performance Optimization

1. **Reduce embedding model size**: Already using `all-MiniLM-L6-v2` (smallest recommended)
2. **Limit context retrieval**: Set `n_results=2-3` for faster queries
3. **Cache frequent queries**: Add Redis for production
4. **Compress ChromaDB**: Enable compression in collection settings

## 📈 Future Improvements

- [ ] Add caching layer (Redis)
- [ ] Implement user authentication
- [ ] Add analytics dashboard
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] WhatsApp integration
- [ ] Booking system integration

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

MIT License - feel free to use for your own projects

## 🙏 Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [ChromaDB](https://www.trychroma.com/)
- [Groq](https://groq.com/)
- [Sentence Transformers](https://www.sbert.net/)

---

Made with ❤️ for CE Tennis Academy