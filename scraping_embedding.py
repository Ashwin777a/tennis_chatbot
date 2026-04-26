from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import chromadb
from sentence_transformers import SentenceTransformer
import os

# -----------------------------
# Configuration
# -----------------------------
BASE_URL = "https://cetennis.in/"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

# -----------------------------
# Initialize Components
# -----------------------------
print("🔄 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("🔄 Connecting to ChromaDB...")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="tennis_data")

# -----------------------------
# Chunking Function
# -----------------------------
def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i + chunk_size]
        if chunk:  # Only add non-empty chunks
            chunks.append(" ".join(chunk))
    
    return chunks

# -----------------------------
# Scrape and Embed Function
# -----------------------------
def scrape_and_embed():
    """Scrape website and directly embed into ChromaDB"""
    
    print(f"🔄 Fetching main page: {BASE_URL}")
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"❌ Failed to fetch main page: {e}")
        return
    
    # Collect all HTML links
    links = set()
    for anchor in soup.find_all("a"):
        href = anchor.get("href")
        if href and ".html" in href:
            full_url = urljoin(BASE_URL, href)
            links.add(full_url)
    
    print(f"📋 Found {len(links)} HTML pages to scrape")
    
    # Counter for document IDs
    doc_id = 0
    successful = 0
    failed = 0
    
    # Process each link
    for idx, link in enumerate(links, 1):
        try:
            print(f"[{idx}/{len(links)}] Processing: {link}")
            
            # Fetch page
            page = requests.get(link, timeout=10)
            page.raise_for_status()
            soup = BeautifulSoup(page.content, "html.parser")
            
            # Extract and clean text
            text = soup.get_text(separator=" ")
            cleaned_text = " ".join(text.split())
            
            # Skip if text is too short
            if len(cleaned_text) < 50:
                print(f"  ⚠️  Skipped (too short)")
                continue
            
            # Create chunks
            chunks = chunk_text(cleaned_text)
            
            if not chunks:
                print(f"  ⚠️  No chunks created")
                continue
            
            # Generate embeddings
            embeddings = model.encode(chunks).tolist()
            
            # Prepare metadata
            page_name = link.split("/")[-1].replace(".html", "")
            ids = [f"id_{doc_id + i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "source": link,
                    "page_name": page_name,
                    "chunk": i,
                    "total_chunks": len(chunks)
                }
                for i in range(len(chunks))
            ]
            
            # Store in ChromaDB
            collection.add(
                documents=chunks,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )
            
            doc_id += len(chunks)
            successful += 1
            print(f"  ✅ Embedded {len(chunks)} chunks")
            
        except requests.RequestException as e:
            failed += 1
            print(f"  ❌ Request error: {e}")
        except Exception as e:
            failed += 1
            print(f"  ❌ Processing error: {e}")
    
    print("\n" + "="*50)
    print(f"🎉 Scraping Complete!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total chunks stored: {doc_id}")
    print("="*50)

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    scrape_and_embed()