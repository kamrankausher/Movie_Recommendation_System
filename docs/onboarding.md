# Internal Onboarding Guide — CineVerse AI

Welcome! This guide will help you understand the project architecture,
set up your development environment, and start contributing.

---

## What This Project Does

CineVerse AI is a **hybrid movie recommendation system** that combines:

1. **Content-Based Filtering (TF-IDF)** — Uses text features (overview, genres, tagline)
   to find similar movies via cosine similarity on a precomputed sparse matrix.

2. **Genre-Based Discovery (TMDB API)** — Uses The Movie Database API to find
   popular movies in the same genre as the selected movie.

The system has two parts:
- **FastAPI Backend** — Serves the recommendation API
- **Streamlit Frontend** — Provides the user interface

---

## Architecture Overview

```
┌─────────────┐     HTTP      ┌──────────────────────────────────┐
│  Streamlit  │ ──────────>   │  FastAPI Backend                 │
│  Frontend   │  <──────────  │                                  │
│  (app.py)   │     JSON      │  ┌───────────┐  ┌────────────┐  │
└─────────────┘               │  │ TF-IDF    │  │ TMDB API   │  │
                              │  │ Recomm.   │  │ Service    │  │
                              │  │ Service   │  │            │  │
                              │  └───────────┘  └────────────┘  │
                              │       │               │         │
                              │  ┌────┴────┐    ┌─────┴─────┐  │
                              │  │ .pkl    │    │ TMDB API  │  │
                              │  │ files   │    │ (external)│  │
                              │  └─────────┘    └───────────┘  │
                              └──────────────────────────────────┘
```

---

## Folder Structure

```
movie-recommendation-system/
├── app/                        # FastAPI backend application
│   ├── main.py                 # App factory + startup (entry point)
│   ├── config.py               # Settings & environment variables
│   ├── models.py               # Pydantic request/response schemas
│   ├── routers/                # Route handlers (one file per domain)
│   │   ├── health.py           # GET /health
│   │   ├── home.py             # GET /home
│   │   ├── movies.py           # GET /movie/id/{id}, GET /movie/search
│   │   ├── recommend.py        # GET /recommend/tfidf, GET /recommend/genre
│   │   └── search.py           # GET /tmdb/search
│   ├── services/               # Business logic
│   │   ├── recommender.py      # TF-IDF similarity computation
│   │   └── tmdb.py             # TMDB API communication
│   └── utils/
│       └── helpers.py          # Shared utility functions
├── tests/                      # Pytest test suite
├── scripts/                    # Benchmark and utility scripts
├── docs/                       # Documentation (this file)
├── frontend/                   # Streamlit UI (optional, app.py in root)
├── df.pkl                      # Preprocessed movie DataFrame (45,447 rows)
├── tfidf_matrix.pkl            # Precomputed TF-IDF sparse matrix
├── tfidf.pkl                   # Fitted TF-IDF vectorizer
├── indices.pkl                 # Title-to-index mapping
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── render.yaml                 # Render deployment config
└── README.md                   # Project README
```

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- TMDB API key (free at https://www.themoviedb.org/settings/api)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/kamrankausher/Movie_Recommendation_System.git
cd Movie_Recommendation_System

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
copy .env.example .env
# Then edit .env and add your TMDB API key

# 5. Start the backend
uvicorn app.main:app --reload --port 8000

# 6. (Optional) Start the frontend
streamlit run app.py
```

---

## API Endpoints

| Method | Path                   | Description                    |
|--------|------------------------|--------------------------------|
| GET    | `/health`              | Health check                   |
| GET    | `/home`                | Home feed movie cards          |
| GET    | `/tmdb/search`         | TMDB keyword search            |
| GET    | `/movie/id/{tmdb_id}`  | Movie details by TMDB ID       |
| GET    | `/movie/search`        | Combined recommendation bundle |
| GET    | `/recommend/tfidf`     | TF-IDF similarity results      |
| GET    | `/recommend/genre`     | Genre-based recommendations    |

---

## How the Recommendation Works

### TF-IDF Pipeline (in `services/recommender.py`)

1. Each movie has a `tags` field = `overview + genres + tagline`
2. These tags are vectorized using `TfidfVectorizer(max_features=50000)`
3. The result is a **sparse matrix** of shape (45,447 × 50,000)
4. For a given movie, we compute cosine similarity against all others
5. Top-N most similar movies are returned

The sparse matrix uses **~18 MB** vs **~17 GB** for a dense equivalent — a **99.9% memory reduction**.

### Genre Pipeline (in `services/tmdb.py`)

1. Fetch the selected movie's genres from TMDB
2. Use TMDB Discover API to find popular movies in the same genre
3. Return as movie cards with posters

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Common Tasks

### Add a new API endpoint
1. Create or edit a router file in `app/routers/`
2. Register it in `app/main.py` with `application.include_router()`
3. Add tests in `tests/`

### Update the dataset
1. Modify the notebook `movie_recommendation_system.ipynb`
2. Re-run all cells to regenerate the `.pkl` files
3. Restart the server

### Deploy to Render
1. Push changes to GitHub
2. Render auto-deploys from the `main` branch
3. Ensure `TMDB_API_KEY` is set in Render environment variables
