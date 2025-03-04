import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from sklearn.metrics.pairwise import cosine_similarity
from ..models.fake_data import get_fake_data

def search_projects(query: str):
    fake_data = get_fake_data()
    final_df = pd.DataFrame(fake_data)

    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)

    final_df["combined_text"] = final_df["project_name"].str.lower() + " " + final_df["project_information"].str.lower()
    texts = final_df["combined_text"].to_list()
    embeddings = model.encode(texts, convert_to_tensor=False)
    embedding_dim = embeddings.shape[1]

    index = faiss.IndexFlatL2(embedding_dim)
    index.add(embeddings)

    query_embedding = model.encode([query.lower()], convert_to_tensor=False)
    top_k = 3
    distances, indices = index.search(query_embedding, top_k)
    recommended_texts = [texts[i] for i in indices[0]]

    similarity_score = []
    for i in range(len(final_df["combined_text"])):
        if final_df["combined_text"][i] in recommended_texts:
            project_info = final_df["combined_text"][i].strip().lower()
            embedding_2 = model.encode([project_info])
            similarity = cosine_similarity(query_embedding, embedding_2)
            similarity_score.append((similarity[0][0], i))
    similarity_score.sort(key=lambda x: x[0], reverse=True)

    results = [fake_data[index] for _, index in similarity_score]
    return results
