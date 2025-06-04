import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from ..services.database_service import project_collection
import os
import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification

model = SentenceTransformer('all-MiniLM-L6-v2')

# Load BERT tokenizer and model once (adjust path as needed)
BEST_RANKING_TF_DIR = os.path.join(os.path.dirname(__file__), '../../best_ranking_tf')
tokenizer = BertTokenizer.from_pretrained(BEST_RANKING_TF_DIR)
bert_rank_model = TFBertForSequenceClassification.from_pretrained(BEST_RANKING_TF_DIR)


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


def get_project_text_for_ranking(project: dict) -> str:
    title = project.get("project_title", "")
    desc = project.get("project_description", "")
    pdf_desc = project.get("project_pdf_description", "")
    return f"{title} {desc} {pdf_desc}"


def rank_projects_with_bert(projects: list) -> list:
    """
    Ranks a list of project dicts using a BERT-based model.
    Returns the full project dict (excluding 'project_description_embedding' and 'project_pdf_description'), 
    sorted by ascending expected rank (lower is better), and adds 'integer_rank' to each project.
    """
    if not projects:
        return []
    texts = [get_project_text_for_ranking(proj) for proj in projects]
    encodings = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=256,
        return_tensors="tf"
    )
    outputs = bert_rank_model(encodings)
    probs = tf.nn.softmax(outputs.logits, axis=1)
    rank_values = tf.constant([1, 2, 3, 4, 5], dtype=tf.float32)
    expected_ranks = tf.reduce_sum(probs * rank_values, axis=1).numpy()
    projects_with_ranks = list(zip(projects, expected_ranks))
    projects_sorted = sorted(projects_with_ranks, key=lambda x: x[1])
    # Return the full project dict (without embedding and pdf_description), plus integer_rank
    result = []
    for idx, (proj, _) in enumerate(projects_sorted):
        proj_copy = {k: v for k, v in proj.items() if k not in ["project_description_embedding", "project_pdf_description"]}
        proj_copy["integer_rank"] = idx + 1
        result.append(proj_copy)
    return result
