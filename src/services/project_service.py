import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from ..services.database_service import project_collection
model = SentenceTransformer('all-MiniLM-L6-v2')


async def fetch_all_projects_in_db() -> list:
    try:
        # Fetch all projects
        projects_cursor = project_collection.find({})
        projects = await projects_cursor.to_list(length=None)  # Fetch all results
        return [
            {
                **project,
                "id": str(project["_id"]),  # Convert _id to string
                "_id": str(project["_id"]),  # Optional: Keep _id as string if needed
            }
            for project in projects
        ]
    except Exception as e:
        raise Exception(f"Error while fetching all projects: {e}")


# Initialize the SentenceTransformer model
async def search_projects_by_description(description: str, top_k: int = 5) -> list:
    try:
        # Fetch all projects from the database
        projects = await fetch_all_projects_in_db()

        # Extract embeddings and project IDs
        embeddings = []
        project_ids = []
        for project in projects:
            if "project_description_embedding" in project and project["project_description_embedding"]:
                embeddings.append(project["project_description_embedding"])
                project_ids.append(project["id"])
            
        print(projects)
        # Convert embeddings to a NumPy array
        embeddings = np.array(embeddings, dtype="float32")

        # Create a FAISS index
        if len(embeddings) == 0:
            raise Exception("No embeddings available for similarity search.")
        dimension = embeddings.shape[1]  # Dimensionality of the embeddings
        index = faiss.IndexFlatL2(dimension)  # L2 distance (Euclidean)
        index.add(embeddings)  # Add embeddings to the index

        # Generate embedding for the input description
        query_embedding = model.encode(description).astype("float32").reshape(1, -1)
        if query_embedding.shape[1] != index.d:
            raise Exception("Query embedding dimensionality does not match the FAISS index.")

        # Adjust top_k if it exceeds the number of embeddings
        top_k = min(top_k, index.ntotal)

        # Perform the search
        distances, indices = index.search(query_embedding, top_k)

        # Retrieve the top-k project IDs and their similarity scores
        results = [
            {"project_id": project_ids[i], "distance": float(distances[0][j])}
            for j, i in enumerate(indices[0])
        ]

        return results
    except Exception as e:
        raise Exception(f"Error during project search: {e}")
