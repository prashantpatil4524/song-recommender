"""
routes/dashboard.py  –  Dataset stats & EDA for the dashboard page
"""

import os
import pandas as pd
from flask import Blueprint, jsonify

dashboard_bp = Blueprint("dashboard", __name__)

SONG_PATH  = os.path.join(os.path.dirname(__file__), "..", "..", "data", "song.xlsx")
GENRE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "data_by_genres.csv")


@dashboard_bp.route("/stats", methods=["GET"])
def stats():
    try:
        df  = pd.read_excel(SONG_PATH)
        df  = df[df["User_Gender"].isin(["Male", "Female"])]

        total       = len(df)
        avg_pop     = round(df["Spotify Popularity"].dropna().mean(), 1)
        avg_age     = round(df["User_age"].dropna().mean(), 1)
        genres_count = df["Gener"].nunique()

        # gender split
        gender = df["User_Gender"].value_counts().to_dict()

        # fav genre distribution (clean)
        fav = df["User_fav_music_genre"].replace({
            "Classical & melody, dance": "Classical",
            "classical": "Classical",
            "Electronic/Dance": "Electronic",
            "Old songs": "Pop",
            "All": "Pop",
            "Kpop": "Pop",
            "trending songs random": "Pop",
            "fav_music_genre": None,
        }).dropna()
        fav_dist = fav.value_counts().to_dict()

        # track genre distribution
        gen_dist = df["Gener"].value_counts().head(10).to_dict()

        # age groups
        bins   = [0, 18, 25, 35, 50, 100]
        labels = ["<18", "18-25", "26-35", "36-50", "50+"]
        df["age_group"] = pd.cut(df["User_age"].dropna(), bins=bins, labels=labels)
        age_dist = df["age_group"].value_counts().sort_index().to_dict()

        # avg popularity by genre
        pop_by_genre = (
            df.groupby("Gener")["Spotify Popularity"]
            .mean()
            .round(1)
            .sort_values(ascending=False)
            .head(10)
            .to_dict()
        )

        return jsonify({
            "total_records":    total,
            "avg_popularity":   avg_pop,
            "avg_user_age":     avg_age,
            "total_genres":     genres_count,
            "gender_split":     gender,
            "fav_genre_dist":   fav_dist,
            "track_genre_dist": gen_dist,
            "age_distribution": age_dist,
            "popularity_by_genre": pop_by_genre,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
