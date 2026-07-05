# 🎵 SongIQ — AI Music Recommendation System

> Predict song popularity & recommend genres using Machine Learning + Flask

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange?logo=scikitlearn)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
![CI/CD](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?logo=githubactions)

---

## 📌 What It Does

| Feature | Description |
|---|---|
| 🤖 **Popularity Predictor** | 6 ML models compete — best accuracy model auto-selected at train time |
| 🎯 **Genre Recommender** | Cosine similarity on 2,973 genres recommends music for each user profile |
| 📊 **Live Dashboard** | EDA charts — gender split, age groups, popularity by genre |
| 🐳 **Docker Ready** | One command to build & run everything |
| ⚙️ **CI/CD Pipeline** | GitHub Actions: train → test → Docker build → deploy |

---

## 🗂️ Project Structure

```
song-recommender/
├── backend/
│   ├── app.py                  # Flask app factory
│   ├── train_model.py          # ML pipeline — trains 6 models, saves best
│   ├── models/                 # Saved .pkl files (auto-generated)
│   └── routes/
│       ├── predict.py          # POST /api/predict
│       ├── recommend.py        # POST /api/recommend
│       └── dashboard.py        # GET  /api/stats
├── frontend/
│   ├── templates/
│   │   ├── index.html          # Landing page
│   │   ├── predict.html        # Prediction form
│   │   ├── recommend.html      # Recommender form + chart
│   │   └── dashboard.html      # EDA dashboard
│   └── static/
│       ├── css/style.css
│       └── js/
│           ├── predict.js
│           ├── recommend.js
│           └── dashboard.js
├── data/
│   ├── song.xlsx               # 4,600 song + user records
│   └── data_by_genres.csv      # 2,973 genre feature vectors
├── .github/
│   └── workflows/ci-cd.yml     # GitHub Actions pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🧠 ML Pipeline

```
song.xlsx
    │
    ▼
Clean & Encode
  • Drop Others/invalid rows
  • Encode gender (Male=1, Female=0)
  • Encode track genre → int
  • Release Date → days since 2020-01-01
  • Fill nulls with median
    │
    ▼
Feature Engineering
  Features: Release_Days, Spotify_Streams, Spotify_Popularity,
            Explicit_Track, Gener, User_age, User_Gender
  Target:   User_fav_music_genre
    │
    ▼
SimpleImputer → StandardScaler → train_test_split (80/20)
    │
    ▼
Train 6 Models in parallel
  ┌─────────────────────┐
  │ Random Forest       │
  │ Gradient Boosting   │
  │ Logistic Regression │
  │ KNN                 │
  │ Decision Tree       │
  │ SVM                 │
  └─────────────────────┘
    │
    ▼
Compare test accuracy + 5-fold cross-validation
    │
    ▼
Best model → saved as best_model.pkl
Scaler, Imputer, LabelEncoder, GenreMap → also saved
    │
    ▼
Flask REST API serves predictions
```

---

## 🚀 Quick Start

### Option 1 — Run Locally (VS Code)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/song-recommender.git
cd song-recommender

# 2. Create virtual environment
python -m venv .venv
source .venv\Scripts\activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train the ML models
python backend/train_model.py

# 5. Start the Flask server
cd backend
python app.py

# 6. Open browser
# http://localhost:5000
```

### Option 2 — Docker (Recommended)

```bash
# Build and run with one command
docker compose up --build

# Open browser
# http://localhost:5000
```

### Option 3 — Docker manual

```bash
docker build -t songiq .
docker run -p 5000:5000 songiq
```

---

## 🔌 API Reference

### `POST /api/predict`
Predict user's favourite music genre.

**Request body:**
```json
{
  "Gener": "Pop",
  "Spotify_Popularity": 72,
  "Spotify_Streams": 500000,
  "Explicit_Track": 0,
  "Release_Days": 365,
  "User_age": 25,
  "User_Gender": 1
}
```

**Response:**
```json
{
  "predicted_genre": "Melody",
  "confidence": 67.3,
  "all_probabilities": { "Melody": 67.3, "Pop": 18.2, "Rap": 8.1 },
  "best_model": "SVM",
  "model_accuracy": 51.4
}
```

---

### `POST /api/recommend`
Get genre recommendations based on user profile.

**Request body:** same as `/api/predict`

**Response:**
```json
{
  "predicted_favourite_genre": "Melody",
  "recommended_genres": [
    { "genres": "indie pop", "popularity": 72.1, "danceability": 0.65 }
  ],
  "top_popular_genres": [
    { "genre": "pop", "avg_popularity": 68.4 }
  ]
}
```

---

### `GET /api/model-info`
Returns all model accuracy scores.

### `GET /api/stats`
Returns EDA stats for the dashboard.

### `GET /api/top-genres`
Returns top 15 genres by popularity.

---

## ⚙️ CI/CD Pipeline (GitHub Actions)

```
Push to main
    │
    ▼
[1] test-and-train
    • Install deps
    • python backend/train_model.py
    • Verify all .pkl files exist
    • Upload artifacts
    │
    ▼
[2] docker-build
    • docker build -t songiq .
    • Smoke test: curl http://localhost:5000/
    │
    ▼
[3] deploy  (main branch only)
    • Push image to Docker Hub
    • Tags: latest + git SHA
```

**Required GitHub Secrets for deploy:**
- `DOCKER_USERNAME` — your Docker Hub username
- `DOCKER_PASSWORD` — your Docker Hub access token

---

## 📊 Dataset

| File | Records | Description |
|---|---|---|
| `song.xlsx` | 4,600 | Track info + user demographics + favourite genre |
| `data_by_genres.csv` | 2,973 | Audio features per genre (acousticness, energy, tempo etc.) |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11, Flask 3.0, Flask-CORS
- **ML:** scikit-learn (RF, GBM, LR, KNN, DT, SVM), pandas, numpy
- **Frontend:** Vanilla JS, Chart.js, CSS3
- **Deploy:** Docker, Docker Compose, GitHub Actions
- **IDE:** VS Code

---

## 📁 VS Code Setup

Install these extensions for the best experience:
- Python (Microsoft)
- Pylance
- Docker
- GitLens
- REST Client (for testing APIs)

Recommended `settings.json`:
```json
{
  "python.defaultInterpreterPath": ".venv/Scripts/python",
  "editor.formatOnSave": true,
  "python.formatting.provider": "black"
}
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — free to use, modify and distribute.
