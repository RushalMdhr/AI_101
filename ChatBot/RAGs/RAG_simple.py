import ollama
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

docs = [
    "My name is Rushal Manandhar",
    "Currently persuing my bachelor degree in Computer Engineering",
    "Currently unemployed and searching for job that matches my skills",
    "My current top skills are MERN stack, AI/ML"
]

def get_embedding(text):
    response = ollama.embeddings(model='all-minilm', prompt=text)
    return response['embedding']

print("Generating embeddings...")
doc_embeddings = [get_embedding(doc) for doc in docs]

# Print the embeddings
print(f"\nGenerated {len(doc_embeddings)} document embeddings")
for i, emb in enumerate(doc_embeddings):
    print(f"Doc {i+1} embedding dimension: {len(emb)}")
    print(f"  First 10 values: {emb[:10]}")
    print(f"  Last 10 values: {emb[-10:]}")
    print()

question = "Who is Rushal and what skills does he have? Is he good enough for working as a full-stack dev"
query_embedding = get_embedding(question)
print(f"\nQuestion embedding dimension: {len(query_embedding)}")
print(f"  First 10 values: {query_embedding[:10]}")

scores = cosine_similarity([query_embedding], doc_embeddings)[0]
print(f"\nSimilarity scores: {scores}")
top_indices = np.argsort(scores)[-2:]
print(f"Top docs: {top_indices}")

context = "\n".join([docs[i] for i in top_indices])
messages = [
    {"role": "system", "content": f"Answer using this context only:\n{context}"},
    {"role": "user", "content": question}
]
response = ollama.chat(model='llama3.2', messages=messages)
print(f"\nFinal answer:\n{response['message']['content']}")