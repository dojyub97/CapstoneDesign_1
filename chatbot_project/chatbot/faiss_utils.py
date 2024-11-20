import faiss
import numpy as np

def build_faiss_index(embeddings):
    dimension = len(embeddings[0]["embedding"])
    index = faiss.IndexFlatL2(dimension)

    vectors = np.array([e["embedding"] for e in embeddings], dtype=np.float32)
    index.add(vectors)
    return index

def search_faiss_index(query_embedding, index, embeddings, top_k=3):
    query_vector = np.array([query_embedding], dtype=np.float32).reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)

    results = []
    for i in range(len(indices[0])):
        idx = indices[0][i]
        results.append({
            "page_num": embeddings[idx]["page_num"],
            "text": embeddings[idx]["text"],
            "distance": distances[0][i],
        })
    return results
