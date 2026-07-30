import ollama, json, numpy as np, os
from sklearn.metrics.pairwise import cosine_similarity

# PDF support
try:
    import PyPDF2
except ImportError:
    print("Install PyPDF2: pip install PyPDF2")

def load_document(file_path):
    """Load text from PDF or TXT"""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    elif ext == ".pdf":
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    
    else:
        raise ValueError("Only .txt and .pdf files supported")

def chunk_text(text, chunk_size=500, overlap=50):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-overlap)]

def get_embedding(text):
    return ollama.embeddings(model='all-minilm', prompt=text)['embedding']

# ===== USAGE =====
# Load your document
file_path = "Power-BI.pdf"  # or sample.txt
raw_text = load_document(file_path)

# Chunk and embed
chunks = chunk_text(raw_text)
data = []
for i, chunk in enumerate(chunks):
    data.append({
        "id": f"chunk_{i}",
        "text": chunk,
        "embedding": get_embedding(chunk),
        "metadata": {"source": os.path.basename(file_path), "chunk": i}
    })

# Save and search
with open("rag_data.json", "w") as f:
    json.dump(data, f)

print(f"✅ Loaded {len(data)} chunks from {file_path}")

# Search function (reuse from previous code)
def search(query, top_k=3):
    q_emb = get_embedding(query)
    scores = [cosine_similarity([q_emb], [item["embedding"]])[0][0] for item in data]
    top_idx = np.argsort(scores)[-top_k:][::-1]
    return [data[i] for i in top_idx]

question = "What is this document about"
results = search(question)
context = "\n\n".join([r["text"] for r in results])

response = ollama.chat(model='llama3.2', messages=[
    {"role": "system", "content": f"Answer using this context:\n{context}"},
    {"role": "user", "content": question}
])

print(f"\n📝 Answer:\n{response['message']['content']}")