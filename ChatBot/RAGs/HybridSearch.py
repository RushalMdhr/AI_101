import ollama, json, numpy as np, math
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt_tab')

# ============ 1. LOAD YOUR DATA ============

with open("datas\\multi_modal_rag.json", "r") as f:
    all_data = json.load(f)

# Extract texts for BM25
doc_texts = [item["text"] for item in all_data]

# ============ 2. BUILD BM25 INDEX ============

# Tokenize documents
tokenized_docs = [word_tokenize(doc.lower()) for doc in doc_texts]
bm25 = BM25Okapi(tokenized_docs)

# ============ 3. HYBRID SEARCH FUNCTION ============

def get_embedding(text):
    return ollama.embeddings(model='nomic-embed-text', prompt=text)['embedding']

def hybrid_search(query, top_k=5, alpha=0.5):
    """
    alpha = weight between vector (0.5) and keyword (0.5)
    alpha=1.0 → pure vector, alpha=0.0 → pure keyword
    """
    
    # 3a. Vector similarity scores
    q_emb = get_embedding(query)
    vector_scores = []
    for item in all_data:
        sim = cosine_similarity([q_emb], [item["embedding"]])[0][0]
        vector_scores.append(sim)
    
    # 3b. BM25 keyword scores
    tokenized_query = word_tokenize(query.lower())
    keyword_scores = bm25.get_scores(tokenized_query)
    
    # 3c. Normalize both to [0, 1] range
    def normalize(scores):
        min_val = min(scores)
        max_val = max(scores)
        if max_val == min_val:
            return [0.5] * len(scores)
        return [(s - min_val) / (max_val - min_val) for s in scores]
    
    norm_vector = normalize(vector_scores)
    norm_keyword = normalize(keyword_scores)
    
    # 3d. Combine scores
    hybrid_scores = [
        alpha * v + (1 - alpha) * k 
        for v, k in zip(norm_vector, norm_keyword)
    ]
    
    # 3e. Get top-k indices
    top_indices = np.argsort(hybrid_scores)[-top_k:][::-1]
    
    return [all_data[i] for i in top_indices]

# ============ 4. GENERATE ANSWER ============

def ask(question, alpha=0.5):
    results = hybrid_search(question, top_k=3, alpha=alpha)
    context = "\n\n".join([r["text"] for r in results])
    
    response = ollama.chat(model='llama3.2', messages=[
        {"role": "system", "content": f"Answer using this context:\n{context}"},
        {"role": "user", "content": question}
    ])
    return response['message']['content']

# ============ 5. TEST IT ============

print("🔍 Hybrid Search Test\n" + "="*30)


# ============ 5. TEST ============
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit": break
    results = hybrid_search(user_input, top_k=2, alpha=0.5)
    print(f"📄 Top contexts: {[r['metadata']['source'] for r in results]}")
    print(f"🤖 Bot : {ask(user_input, alpha=0.5)}...")
    # print(f"Bot: {ask(user_input)}")

# test_queries = [
#     "What is RAG?",
#     "Toyota Camry price",
#     "who won World Cup 2026"
# ]

# for q in test_queries:
#     print(f"\n❓ Query: {q}")
#     results = hybrid_search(q, top_k=2, alpha=0.5)
#     print(f"📄 Top contexts: {[r['metadata']['source'] for r in results]}")
#     print(f"🤖 Answer: {ask(q, alpha=0.5)[:200]}...")