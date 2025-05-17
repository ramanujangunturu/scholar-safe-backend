import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from ..services.database_service import project_collection

model = SentenceTransformer('all-MiniLM-L6-v2')


async def fetch_all_projects_in_db() -> list:
    try:
        projects_cursor = project_collection.find({})
        projects = await projects_cursor.to_list(length=None)
        return [
            {
                **project,
                "id": str(project["_id"]),
                "_id": str(project["_id"]),
            }
            for project in projects
        ]
    except Exception as e:
        raise Exception(f"Error while fetching all projects: {e}")


async def search_projects_by_description(description: str, top_k: int = 5) -> list:
    try:
        # Fetch all projects
        projects = await fetch_all_projects_in_db()

        # Extract embeddings and project IDs
        embeddings = []
        project_ids = []
        for project in projects:
            if "project_description_embedding" in project and project["project_description_embedding"]:
                embeddings.append(project["project_description_embedding"])
                project_ids.append(project["id"])

        if len(embeddings) == 0:
            raise Exception("No embeddings available for similarity search.")

        # Convert and normalize embeddings (cosine similarity)
        embeddings = np.array(embeddings, dtype="float32")
        faiss.normalize_L2(embeddings)

        # Create a FAISS index for inner product (cosine similarity after normalization)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        # Generate and normalize query embedding
        query_embedding = model.encode(description).astype("float32").reshape(1, -1)
        faiss.normalize_L2(query_embedding)

        # Adjust top_k if it exceeds the number of entries
        top_k = min(top_k, index.ntotal)

        # Perform search (inner product ≈ cosine similarity)
        distances, indices = index.search(query_embedding, top_k)

        # Retrieve the top-k project IDs and similarity scores
        results = [
            {"project_id": project_ids[i], "similarity": float(distances[0][j])}
            for j, i in enumerate(indices[0])
        ]

        return results
    except Exception as e:
        raise Exception(f"Error during project search: {e}")
