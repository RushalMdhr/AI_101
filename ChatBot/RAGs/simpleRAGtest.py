import ollama, numpy as np, os
from opentelemetry import context
from sklearn.metrics.pairwise import cosine_similarity

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
file_path = "sources\\sample.txt"  # or sample.txt 
raw_text = load_document(file_path)

# Chunk and embed
chunks = chunk_text(raw_text)
all_data = []
for i, chunk in enumerate(chunks):
    all_data.append({
        "id": f"chunk_{i}",
        "text": chunk,
        "embedding": get_embedding(chunk),
        "metadata": {"source": os.path.basename(file_path), "chunk": i}
    })


def search(query,top=2):
    q_emb = get_embedding(query)
    scores = [cosine_similarity([q_emb], [item["embedding"]])[0][0] for item in all_data]
    top_idx = np.argsort(scores)[-top:][::-1]
    return [all_data[i] for i in top_idx if scores[i] > 0]

def ask(question,use_memory=None):
    if use_memory:
        results = search(question)
        context = "\n\n".join([r["text"] for r in results])
        # context = "my name is bob and I like to play football"
        messages[0]["content"] = f"Answer using this context:\n{context}"

    messages.append({"role": "user", "content": question})
    response = ollama.chat(model='llama3.2', messages=messages)
    return response['message']['content']
    return f"{question} : {use_memory} : {messages}"

messages = [{"role": "system", "content": "You are a helpful assistant"}]
while True:
    use_memory=None
    user_input = input("user : ")
    if user_input.lower() == "exit": break
    if user_input.lower() == "use memory":
        use_memory = True
        user_input = input("enter your question: ")
    print(f"bot : {ask(user_input,use_memory)}")