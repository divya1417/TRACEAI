import os
import pickle
import json
import traceback
import warnings
from collections import defaultdict

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


warnings.filterwarnings(action="ignore")


from pages.helper import db_queries
from pages.helper.data_models import RegisteredCases, PublicSubmissions
from sqlmodel import Session, select


def get_public_cases_data(status="NF"):
    try:
        result = db_queries.fetch_public_cases(train_data=True, status=status)
        d1 = pd.DataFrame(result, columns=["label", "face_mesh"])
        d1["face_mesh"] = d1["face_mesh"].apply(lambda x: json.loads(x))
        d2 = pd.DataFrame(d1.pop("face_mesh").values.tolist(), index=d1.index).rename(
            columns=lambda x: "fm_{}".format(x + 1)
        )
        df = d1.join(d2)
        # Ensure all columns except label are float
        for col in df.columns:
            if col != "label":
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    except Exception as e:
        traceback.print_exc()
        return None


def get_registered_cases_data(status="NF"):
    try:
        with Session(db_queries.engine) as session:
            result = session.exec(
                select(
                    RegisteredCases.id,
                    RegisteredCases.face_mesh,
                    RegisteredCases.status,
                )
            ).all()
            d1 = pd.DataFrame(result, columns=["label", "face_mesh", "status"])
            if status:
                d1 = d1[d1["status"] == status]
            d1["face_mesh"] = d1["face_mesh"].apply(lambda x: json.loads(x))
            d2 = pd.DataFrame(
                d1.pop("face_mesh").values.tolist(), index=d1.index
            ).rename(columns=lambda x: "fm_{}".format(x + 1))
            df = d1.join(d2)
            # Ensure all columns except label and status are float
            for col in df.columns:
                if col not in ["label", "status"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            return df
    except Exception as e:
        traceback.print_exc()
        return None


def _get_embedding_cases(table_class, status="NF"):
    """Fetch id and face_embedding for cases that have embeddings."""
    try:
        with Session(db_queries.engine) as session:
            result = session.exec(
                select(table_class.id, table_class.face_embedding)
                .where(table_class.status == status)
            ).all()
            # Filter to only cases with valid embeddings
            valid_cases = []
            for r in result:
                if r[1]:
                    try:
                        emb = json.loads(r[1])
                        if isinstance(emb, list) and len(emb) > 0:
                            valid_cases.append((r[0], r[1]))
                    except:
                        pass
            return valid_cases
    except Exception as e:
        traceback.print_exc()
        return []


from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder


def match_with_embeddings(similarity_threshold=0.18):
    """Match using DeepFace 512-d face embeddings and cosine similarity.
    Handles frontal faces AND side profiles."""
    matched_images = defaultdict(list)

    pub_cases = _get_embedding_cases(PublicSubmissions, status="NF")
    reg_cases = _get_embedding_cases(RegisteredCases, status="NF")

    if not pub_cases or not reg_cases:
        return None  # No embedding data, caller should fall back

    pub_ids = [c[0] for c in pub_cases]
    reg_ids = [c[0] for c in reg_cases]

    pub_embeddings = np.array([json.loads(c[1]) for c in pub_cases])
    reg_embeddings = np.array([json.loads(c[1]) for c in reg_cases])

    sim_matrix = cosine_similarity(pub_embeddings, reg_embeddings)

    for i, pub_id in enumerate(pub_ids):
        best_idx = np.argmax(sim_matrix[i])
        best_sim = sim_matrix[i][best_idx]
        print(f"Embedding similarity for {pub_id}: {best_sim:.4f}")

        if best_sim >= similarity_threshold:
            reg_id = reg_ids[best_idx]
            matched_images[reg_id].append(pub_id)

    return {"status": True, "result": matched_images}


def match(distance_threshold=1.0):
    """Match public submissions against registered cases.
    Tries embedding-based matching first (supports side profiles),
    falls back to KNN on landmarks for backward compatibility."""

    # Try embedding-based matching first
    embedding_result = match_with_embeddings()
    if embedding_result is not None:
        return embedding_result

    # Fallback: KNN on MediaPipe landmarks (frontal faces only)
    matched_images = defaultdict(list)
    public_cases_df = get_public_cases_data()
    registered_cases_df = get_registered_cases_data()

    if public_cases_df is None or registered_cases_df is None:
        return {"status": False, "message": "Couldn't connect to database"}
    if len(public_cases_df) == 0 or len(registered_cases_df) == 0:
        return {"status": False, "message": "No public or registered cases found"}

    # Store original labels before encoding
    original_reg_labels = registered_cases_df.iloc[:, 0].tolist()
    original_pub_labels = public_cases_df.iloc[:, 0].tolist()

    # Prepare training data
    reg_features = registered_cases_df.iloc[:, 2:].values.astype(float)
    numeric_labels = list(range(len(reg_features)))

    knn = KNeighborsClassifier(n_neighbors=1, algorithm="ball_tree", weights="distance")
    knn.fit(reg_features, numeric_labels)

    for i, row in public_cases_df.iterrows():
        pub_label = original_pub_labels[i]
        face_encoding = np.array(row[1:]).astype(float)

        try:
            closest_distances = knn.kneighbors([face_encoding])[0][0]
            closest_distance = np.min(closest_distances)
            print(f"Distance for case {pub_label}: {closest_distance}")

            if closest_distance <= distance_threshold:
                predicted_idx = knn.predict([face_encoding])[0]
                reg_label = original_reg_labels[predicted_idx]
                matched_images[reg_label].append(pub_label)
        except Exception as e:
            print(f"Error processing public case {pub_label}: {str(e)}")
            continue

    return {"status": True, "result": matched_images}


if __name__ == "__main__":
    result = match()
    print(result)
