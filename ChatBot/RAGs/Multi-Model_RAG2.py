import ollama, json, numpy as np, os
from sklearn.metrics.pairwise import cosine_similarity
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

link = "sources\\Power-BI.pdf"
# ============ 1. LOAD + CHUNK WITH DOCLING ============

# def load_and_chunk_with_docling(file_path):
#     converter = DocumentConverter()
#     result = converter.convert(file_path)
#     doc = result.document
    
#     # Get raw text
#     raw_text = doc.export_to_text()
    
#     # Docling's chunker
#     chunker = HybridChunker(max_size=500, overlap=50)
#     chunks = chunker.chunk(doc)
    
#     chunk_data = []
#     for i, chunk in enumerate(chunks):
#         # Fix: Access metadata correctly
#         meta = chunk.metadata if hasattr(chunk, 'metadata') else {}
        
#         chunk_data.append({
#             "text": chunk.text,
#             "metadata": {
#                 "source": os.path.basename(file_path),
#                 "page": meta.get("page", 0) if isinstance(meta, dict) else 0,
#                 "heading": meta.get("heading", "") if isinstance(meta, dict) else "",
#                 "chunk_index": i
#             }
#         })
    
#     return chunk_data
def chunk_text(text, chunk_size=500, overlap=50):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-overlap)]

def load_docling_simple(file_path):
    converter = DocumentConverter()
    result = converter.convert(file_path)
    doc = result.document
    return doc.export_to_text()

# Then use your existing chunk_text() function
raw_text = load_docling_simple(link)
chunks = chunk_text(raw_text)  # Your existing chunking

# ============ 2. EMBED + STORE ============

def get_embedding(text):
    return ollama.embeddings(model='nomic-embed-text', prompt=text)['embedding']

# Load your PDF/document
# chunks = load_and_chunk_with_docling(link)

all_data = []
for chunk in chunks:
    all_data.append({
        "text": int(chunk["text"]),
        "embedding": get_embedding(chunk["text"]),
        "metadata": chunk["metadata"]
    })

# Save
with open("docling_rag.json", "w") as f:
    json.dump(all_data, f, indent=2)

print(f"✅ Loaded {len(all_data)} chunks with Docling")

# ============ 3. SEARCH + GENERATE ============

def search(query, top_k=3):
    q_emb = get_embedding(query)
    scores = [cosine_similarity([q_emb], [item["embedding"]])[0][0] for item in all_data]
    top_idx = np.argsort(scores)[-top_k:][::-1]
    return [all_data[i] for i in top_idx if scores[i] > 0]

def ask(question):
    results = search(question)
    context = "\n\n".join([f"[Source: {r['metadata']['source']}, Page: {r['metadata']['page']}]\n{r['text']}" for r in results])
    
    response = ollama.chat(model='llama3.2', messages=[
        {"role": "system", "content": f"Answer using this context. Cite sources:\n{context}"},
        {"role": "user", "content": question}
    ])
    return response['message']['content']

# Test
print(ask("What does this document say about?"))