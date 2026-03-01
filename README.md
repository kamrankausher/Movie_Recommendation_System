🎬 CineVerse AI — Movie Recommendation System

AI-Powered Hybrid Movie Recommendation System using TF-IDF + TMDB API
Deployed with FastAPI (Render) + Streamlit (Cloud)

🌐 Live Demo

Frontend (Streamlit):
👉 https://movierecommendationsystem-8m8wezfpsucndtz8xuuh7d.streamlit.app/

Backend (FastAPI – Render):
👉 Deployed on Render (Private API Service)

🚀 Overview

CineVerse AI is a full-stack movie recommendation system that combines:

🔎 Content-based filtering (TF-IDF + Cosine Similarity)

🎭 Genre-based recommendations (TMDB Discover API)

🎬 Live movie metadata from TMDB

⚡ FastAPI backend

🎨 Premium Streamlit frontend

The system provides:

Trending movies

Search suggestions

Movie details

Similar movies (TF-IDF)

Genre-based recommendations

🧠 Recommendation Architecture
1️⃣ Content-Based (TF-IDF)

Preprocessed movie metadata

TF-IDF vectorization

Cosine similarity computation

Precomputed sparse matrix

Real-time similarity scoring

Used for:
Similar Movies (Content Based)

2️⃣ Genre-Based (TMDB Discover API)

Fetch selected movie genre

Query TMDB discover endpoint

Filter out current movie

Return popular movies in same genre

Used for:
More Like This (Genre)

🏗️ Tech Stack
🔹 Backend

FastAPI

Uvicorn

httpx

Pandas

NumPy

Scikit-learn

Pickle (Precomputed TF-IDF matrix)

TMDB API

🔹 Frontend

Streamlit

Custom CSS (Glassmorphism + Premium UI)

Responsive grid layout

🔹 Deployment

Render (FastAPI backend)

Streamlit Cloud (Frontend)

📁 Project Structure
movie-recommendation-system/
│
├── main.py                  # FastAPI backend
├── app.py                   # Streamlit frontend
├── df.pkl                   # Cleaned movie dataset
├── tfidf.pkl                # TF-IDF vectorizer
├── tfidf_matrix.pkl         # Sparse matrix
├── indices.pkl              # Title-to-index mapping
├── movies_metadata.csv      # Raw dataset
├── requirements.txt
└── README.md

⚙️ How It Works (Flow)

User opens Streamlit app

Frontend calls FastAPI backend

Backend:

Fetches movie data from TMDB

Runs TF-IDF similarity

Returns combined recommendation bundle

Frontend renders posters + details

🧪 Local Setup
1️⃣ Clone Repository

git clone https://github.com/yourusername/movie-recommendation-system.git
cd movie-recommendation-system

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt
pip install uvicorn fastapi python-dotenv httpx

4️⃣ Add TMDB API Key

Create .env file:
TMDB_API_KEY=your_tmdb_api_key_here

Get API key from:
https://www.themoviedb.org/settings/api

5️⃣ Run Backend
uvicorn main:app --reload

6️⃣ Run Frontend

In new terminal:
streamlit run app.py

🌍 Deployment Architecture
🔹 Backend (Render)

Deployed as Web Service

Environment variable:
TMDB_API_KEY=xxxx

Auto deploy from GitHub

🔹 Frontend (Streamlit Cloud)

Connected to GitHub

app.py as entry file

API_BASE updated to Render URL

🔥 Features

✔ Trending Movies
✔ Popular / Top Rated / Upcoming
✔ Real-time TMDB search
✔ Content-based similarity
✔ Genre recommendations
✔ Premium UI
✔ Fully deployed production app
✔ Clean REST API structure

📊 Recommendation Logic

Cosine Similarity:
similarity = (TFIDF_matrix @ query_vector.T)

Sorted by highest score excluding self-match.

🎯 Why This Project Matters

This project demonstrates:

End-to-end ML deployment

Real-world API integration

Backend + Frontend architecture

Production-level deployment

Clean code separation

Efficient sparse matrix handling

Hybrid recommendation system design

🏆 Future Improvements

Collaborative Filtering

User Authentication

Watchlist system

Caching layer (Redis)

Pagination

Dockerized deployment

React frontend (Netflix-level UI)

👨‍💻 Author

Kamran Kausher
B.Tech CSE | AI/ML Enthusiast
Building production-grade ML systems.