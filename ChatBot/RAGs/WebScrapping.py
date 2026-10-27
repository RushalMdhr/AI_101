import ollama, json, numpy as np, os, requests
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import pdfplumber

def chunk_text(text, chunk_size=500, overlap=50):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-overlap)]

def get_embedding(text):
    return ollama.embeddings(model='all-minilm', prompt=text)['embedding']

def load_website(url):
    headers = {
        'User-Agent': 'RAGBot/1.0 (https://yourwebsite.com; your_email@example.com)'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text(separator="\n", strip=True)


link = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"
raw_text = load_website(link)
print(f"________________ RAW TEXT ________________\n{raw_text}\n")
chunks = chunk_text(raw_text)

all_data = []
for i, chunk in enumerate(chunks):
        all_data.append({
            "text": chunk,
            "embedding": get_embedding(chunk),
            "metadata": {
                "source": link,
                # "type": "web" if link.startswith("http") else "image" if link.endswith(('.png','.jpg')) else "pdf",
                "type": "web",
                "chunk": i
            }
        })

# Save
with open("WebScrapTestWithIndent2.json", "w") as f:
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

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit": break
    print(f"Bot: {ask(user_input)}")


