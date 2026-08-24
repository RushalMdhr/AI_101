import ollama, json, numpy as np, os, requests
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import pdfplumber

# ============ 1. LOADERS ============
def load_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)

def load_image(file_path):
    # OCR with Tesseract
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)

def load_website(url):
    headers = {
        'User-Agent': 'RAGBot/1.0 (https://yourwebsite.com; your_email@example.com)'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text(separator="\n", strip=True)

def load_document(source):
    """Auto-detect type and load"""
    if source.startswith("http"):
        return load_website(source)
    elif source.lower().endswith(('.png', '.jpg', '.jpeg')):
        return load_image(source)
    elif source.lower().endswith('.pdf'):
        return load_pdf(source)
    else:
        with open(source, 'r', encoding='utf-8') as f:
            return f.read()

# ============ 2. CHUNK + EMBED ============
def chunk_text(text, chunk_size=500, overlap=50):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-overlap)]

def get_embedding(text):
    return ollama.embeddings(model='nomic-embed-text', prompt=text)['embedding']

# ============ 3. BUILD DATABASE ============
sources = [
    "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup",
    "sources\\RushalMananadhar(790333).pdf",
    "sources/Image.jpg", # Add your image
    "sources/sample.txt"  # Add your JSON file
    # "https://en.wikipedia.org/wiki/Cristiano_Ronaldo",
]

all_data = []
for src in sources:
    print(f"📥 Loading: {src}")
    raw_text = load_document(src)
    print(f"________________ RAW TEXT ________________\n{raw_text}\n")
    chunks = chunk_text(raw_text)
    
    for i, chunk in enumerate(chunks):
        all_data.append({
            "text": chunk,
            "embedding": get_embedding(chunk),
            "metadata": {
                "source": src,
                "type": "web" if src.startswith("http") else "image" if src.endswith(('.png','.jpg')) else "pdf",
                "chunk": i
            }
        })

# Save
with open("datas\\multi_modal_rag.json", "w") as f:
    json.dump(all_data, f, indent=2)
print(f"✅ Saved {len(all_data)} chunks")

# ============ 4. SEARCH + GENERATE ============
def search(query, top_k=3):
    q_emb = get_embedding(query)
    scores = [cosine_similarity([q_emb], [item["embedding"]])[0][0] for item in all_data]
    top_idx = np.argsort(scores)[-top_k:][::-1]
    return [all_data[i] for i in top_idx if scores[i] > 0]

def ask(question):
    results = search(question)
    context = "\n\n".join([r["text"] for r in results])
    
    response = ollama.chat(model='llama3.2', messages=[
        {"role": "system", "content": f"Answer using this context:\n{context}"},
        {"role": "user", "content": question}
    ])
    return response['message']['content']

# ============ 5. TEST ============
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit": break
    print(f"Bot: {ask(user_input)}")