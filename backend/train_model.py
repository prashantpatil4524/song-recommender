"""
train_model.py
Trains multiple classifiers on song.xlsx, picks the best by accuracy,
saves the model + scaler + label encoder to backend/models/
"""

import os
import pickle
import warnings
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.impute import SimpleImputer

warnings.filterwarnings("ignore")

DATA_PATH   = os.path.join(os.path.dirname(__file__), "..", "data", "song.xlsx")
MODELS_DIR  = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def load_and_clean(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)

    # ── drop header-duplicate rows & fix gender
    df = df[df["User_Gender"].isin(["Male", "Female"])]
    df["User_Gender"] = df["User_Gender"].map({"Male": 1, "Female": 0})

    # ── clean target label
    replace_map = {
        "Classical & melody, dance": "Classical",
        "classical":                 "Classical",
        "Electronic/Dance":          "Electronic",
        "Old songs":                 "Pop",
        "All":                       "Pop",
        "Kpop":                      "Pop",
        "trending songs random":     "Pop",
        "fav_music_genre":           None,
    }
    df["User_fav_music_genre"] = df["User_fav_music_genre"].replace(replace_map)
    df = df[df["User_fav_music_genre"].notna()]

    # ── encode Gener (track genre)
    genre_map = {g: i for i, g in enumerate(df["Gener"].dropna().unique())}
    df["Gener"] = df["Gener"].map(genre_map).fillna(-1)

    # ── release date → numeric (days since epoch)
    df["Release Date"] = pd.to_datetime(df["Release Date"], errors="coerce")
    df["Release_Days"] = (df["Release Date"] - pd.Timestamp("2020-01-01")).dt.days
    df.drop(columns=["Release Date", "Track"], inplace=True)

    # ── fill numeric nulls
    df["Spotify Streams"]    = df["Spotify Streams"].fillna(df["Spotify Streams"].median())
    df["Spotify Popularity"] = df["Spotify Popularity"].fillna(df["Spotify Popularity"].median())

    return df, genre_map


def train():
    print("📂  Loading data …")
    df, genre_map = load_and_clean(DATA_PATH)

    # ── features & target
    FEATURES = ["Release_Days", "Spotify Streams", "Spotify Popularity",
                "Explicit Track", "Gener", "User_age", "User_Gender"]
    X = df[FEATURES]
    y = df["User_fav_music_genre"]

    # encode target
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # impute + scale
    imputer = SimpleImputer(strategy="mean")
    X_imp   = imputer.fit_transform(X)

    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X_imp)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    # ── manual random oversampling to handle class imbalance in the training set
    df_train = pd.DataFrame(X_train)
    df_train['target'] = y_train
    max_size = df_train['target'].value_counts().max()
    resampled = []
    for label, group in df_train.groupby('target'):
        resampled.append(group.sample(max_size, replace=True, random_state=42))
    df_resampled = pd.concat(resampled, axis=0)
    X_train_res = df_resampled.drop(columns=['target']).values
    y_train_res = df_resampled['target'].values

    # ── candidate models
    candidates = {
        "Random Forest":         RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
        "Gradient Boosting":     GradientBoostingClassifier(n_estimators=150, random_state=42),
        "Logistic Regression":   LogisticRegression(max_iter=500, random_state=42),
        "K-Nearest Neighbors":   KNeighborsClassifier(n_neighbors=7),
        "Decision Tree":         DecisionTreeClassifier(max_depth=10, random_state=42),
        "SVM":                   SVC(probability=True, random_state=42),
    }

    results = {}
    print("\n🏋️  Training models …\n")
    for name, model in candidates.items():
        # Fit on oversampled training data
        model.fit(X_train_res, y_train_res)
        y_pred = model.predict(X_test)
        acc    = accuracy_score(y_test, y_pred)
        f1     = f1_score(y_test, y_pred, average="macro")
        # Use balanced_accuracy for cross-validation score to reflect performance on all classes
        cv     = cross_val_score(model, X_scaled, y_enc, cv=5, scoring="balanced_accuracy").mean()
        results[name] = {"model": model, "accuracy": acc, "cv_accuracy": cv, "f1_macro": f1}
        print(f"  {name:<25}  acc={acc:.4f}  f1_macro={f1:.4f}  cv={cv:.4f}")

    # ── pick best by macro F1-score to ensure class diversity
    best_name = max(results, key=lambda n: results[n]["f1_macro"])
    best      = results[best_name]
    print(f"\n✅  Best model: {best_name}  (acc={best['accuracy']:.4f}, f1_macro={best['f1_macro']:.4f})")
    print(classification_report(y_test, best["model"].predict(X_test),
                                target_names=le.classes_))

    # ── persist everything
    pickle.dump(best["model"], open(os.path.join(MODELS_DIR, "best_model.pkl"),  "wb"))
    pickle.dump(scaler,        open(os.path.join(MODELS_DIR, "scaler.pkl"),      "wb"))
    pickle.dump(imputer,       open(os.path.join(MODELS_DIR, "imputer.pkl"),     "wb"))
    pickle.dump(le,            open(os.path.join(MODELS_DIR, "label_encoder.pkl"), "wb"))
    pickle.dump(genre_map,     open(os.path.join(MODELS_DIR, "genre_map.pkl"),   "wb"))

    # save results summary
    summary = {n: {"accuracy": v["accuracy"], "cv_accuracy": v["cv_accuracy"]}
               for n, v in results.items()}
    summary["best"] = best_name
    pickle.dump(summary, open(os.path.join(MODELS_DIR, "model_results.pkl"), "wb"))

    print("\n💾  Models saved to backend/models/")
    return summary


if __name__ == "__main__":
    train()
