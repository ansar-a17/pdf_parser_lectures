from sentence_transformers import SentenceTransformer
from typing import List

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_transcripts(lines: List):
    embeddings = model.encode(lines)
    return embeddings

def embed_single(line: str):
    embedding = model.encode(line)
    return embedding

"""
from sklearn.metrics.pairwise import cosine_similarity
similarity = cosine_similarity([embeddings[0]], [embeddings[2]])[0][0]
print(f"\nSimilarity between text 1 and 3: {similarity:.4f}")
"""