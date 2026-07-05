"""
routes/recommend.py  –  Song & genre recommendation endpoint
Uses data_by_genres.csv (cosine similarity) + model prediction
"""

import os, pickle
import numpy as np
import pandas as pd
from flask import Blueprint, request, jsonify
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

recommend_bp = Blueprint("recommend", __name__)

DATA_PATH  = os.path.join(os.path.dirname(__file__), "..", "..", "data", "data_by_genres.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

# cache
_genre_df     = None
_sim_matrix   = None
_sim_scaler   = None


def _load_genre_data():
    global _genre_df, _sim_matrix, _sim_scaler
    if _genre_df is None:
        df = pd.read_csv(DATA_PATH)
        df = df.dropna(subset=["popularity"])
        df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)

        features = ["acousticness", "danceability", "energy",
                    "instrumentalness", "liveness", "loudness",
                    "speechiness", "tempo", "valence", "popularity"]

        feat_df = df[features].fillna(0)
        _sim_scaler  = StandardScaler()
        feat_scaled  = _sim_scaler.fit_transform(feat_df)
        _sim_matrix  = cosine_similarity(feat_scaled)
        _genre_df    = df.reset_index(drop=True)

    return _genre_df, _sim_matrix


@recommend_bp.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()

        # ── 1. use the ML model to predict favourite genre
        model   = pickle.load(open(os.path.join(MODELS_DIR, "best_model.pkl"),    "rb"))
        scaler  = pickle.load(open(os.path.join(MODELS_DIR, "scaler.pkl"),        "rb"))
        imputer = pickle.load(open(os.path.join(MODELS_DIR, "imputer.pkl"),       "rb"))
        le      = pickle.load(open(os.path.join(MODELS_DIR, "label_encoder.pkl"), "rb"))
        gmap    = pickle.load(open(os.path.join(MODELS_DIR, "genre_map.pkl"),     "rb"))

        genre_encoded = gmap.get(data.get("Gener", "Pop"), -1)
        COLS = [
            "Release_Days", "Spotify Streams", "Spotify Popularity",
            "Explicit Track", "Gener", "User_age", "User_Gender"
        ]
        features_df = pd.DataFrame(
            [[
                float(data.get("Release_Days",        365)),
                float(data.get("Spotify_Streams",     500000)),
                float(data.get("Spotify_Popularity",  70)),
                int(data.get("Explicit_Track",        0)),
                float(genre_encoded),
                float(data.get("User_age",            25)),
                int(data.get("User_Gender",           1)),
            ]],
            columns=COLS
        )

        X_imp     = imputer.transform(features_df)
        X_scaled  = scaler.transform(X_imp)
        pred_enc  = model.predict(X_scaled)[0]
        pred_genre = le.inverse_transform([pred_enc])[0]

        # ── 2. recommend genres from CSV using cosine similarity
        df, sim_matrix = _load_genre_data()

        # find genres whose name partially matches the predicted genre
        mask = df["genres"].str.lower().str.contains(pred_genre.lower(), na=False)
        if not mask.any():
            # fallback: top popular genres
            mask = df["popularity"] > df["popularity"].quantile(0.7)

        seed_idx = df[mask].index.tolist()

        scores = sim_matrix[seed_idx].mean(axis=0)
        top_idx = np.argsort(scores)[::-1][:10]

        recommended = df.iloc[top_idx][["genres", "popularity", "danceability",
                                         "energy", "valence", "tempo"]].copy()
        recommended["popularity"]   = recommended["popularity"].round(1)
        recommended["danceability"] = recommended["danceability"].round(3)
        recommended["energy"]       = recommended["energy"].round(3)
        recommended["valence"]      = recommended["valence"].round(3)
        recommended["tempo"]        = recommended["tempo"].round(1)

        # ── 3. top popular genres overall for chart
        top_popular = (
            df.groupby("genres")["popularity"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
            .rename(columns={"genres": "genre", "popularity": "avg_popularity"})
        )
        top_popular["avg_popularity"] = top_popular["avg_popularity"].round(1)

        return jsonify({
            "predicted_favourite_genre": pred_genre,
            "recommended_genres":        recommended.to_dict(orient="records"),
            "top_popular_genres":        top_popular.to_dict(orient="records"),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@recommend_bp.route("/top-genres", methods=["GET"])
def top_genres():
    try:
        df, _ = _load_genre_data()
        top = (
            df.groupby("genres")["popularity"]
            .mean()
            .sort_values(ascending=False)
            .head(15)
            .reset_index()
        )
        top["popularity"] = top["popularity"].round(1)
        return jsonify(top.rename(columns={"genres": "genre"}).to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
