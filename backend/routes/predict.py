"""
routes/predict.py  -  Popularity prediction endpoint
"""

import os
import pickle
import numpy as np
import pandas as pd
from flask import Blueprint, request, jsonify

predict_bp = Blueprint("predict", __name__)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


def _load():
    model   = pickle.load(open(os.path.join(MODELS_DIR, "best_model.pkl"),    "rb"))
    scaler  = pickle.load(open(os.path.join(MODELS_DIR, "scaler.pkl"),        "rb"))
    imputer = pickle.load(open(os.path.join(MODELS_DIR, "imputer.pkl"),       "rb"))
    le      = pickle.load(open(os.path.join(MODELS_DIR, "label_encoder.pkl"), "rb"))
    gmap    = pickle.load(open(os.path.join(MODELS_DIR, "genre_map.pkl"),     "rb"))
    results = pickle.load(open(os.path.join(MODELS_DIR, "model_results.pkl"), "rb"))
    return model, scaler, imputer, le, gmap, results


@predict_bp.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        model, scaler, imputer, le, gmap, results = _load()

        genre_encoded = gmap.get(data.get("Gener", "Pop"), -1)

        COLS = [
            "Release_Days", "Spotify Streams", "Spotify Popularity",
            "Explicit Track", "Gener", "User_age", "User_Gender"
        ]

        features = pd.DataFrame(
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

        X_imp    = imputer.transform(features)
        X_scaled = scaler.transform(X_imp)

        pred_enc   = model.predict(X_scaled)[0]
        pred_prob  = model.predict_proba(X_scaled)[0]
        pred_label = le.inverse_transform([pred_enc])[0]

        classes_proba = {
            le.inverse_transform([i])[0]: round(float(p) * 100, 2)
            for i, p in enumerate(pred_prob)
        }

        return jsonify({
            "predicted_genre":   pred_label,
            "confidence":        round(float(max(pred_prob)) * 100, 2),
            "all_probabilities": classes_proba,
            "best_model":        results["best"],
            "model_accuracy":    round(results[results["best"]]["accuracy"] * 100, 2),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@predict_bp.route("/model-info", methods=["GET"])
def model_info():
    try:
        results = pickle.load(open(os.path.join(MODELS_DIR, "model_results.pkl"), "rb"))
        best    = results.pop("best")
        models_list = [
            {
                "name":        name,
                "accuracy":    round(v["accuracy"] * 100, 2),
                "cv_accuracy": round(v["cv_accuracy"] * 100, 2),
                "is_best":     name == best,
            }
            for name, v in results.items()
        ]
        models_list.sort(key=lambda x: x["accuracy"], reverse=True)
        return jsonify({"best_model": best, "models": models_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
