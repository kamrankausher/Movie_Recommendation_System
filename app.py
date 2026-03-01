import requests
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="CineVerse AI", page_icon="🎬", layout="wide")

# =============================
# PREMIUM GLOBAL STYLING
# =============================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 20% 20%, #111827 0%, #000000 70%);
    color: #f3f4f6;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #020617);
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* Titles */
.main-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    color: #9ca3af;
    margin-bottom: 2rem;
}

/* Card */
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 12px;
    transition: all 0.35s ease;
    border: 1px solid rgba(255,255,255,0.08);
}

.glass-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 25px 40px rgba(0,0,0,0.6);
}

/* Poster Hover */
img {
    border-radius: 14px;
    transition: transform 0.35s ease;
}

img:hover {
    transform: scale(1.05);
}

/* Movie title */
.movie-title {
    font-size: 0.95rem;
    font-weight: 600;
    margin-top: 8px;
    min-height: 42px;
}

/* Buttons */
.stButton>button {
    border-radius: 30px;
    background: linear-gradient(90deg,#6366f1,#a855f7);
    color: white;
    font-weight: 600;
    border: none;
    padding: 0.4rem 1rem;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 18px rgba(168,85,247,0.7);
}

/* Section Title */
.section-title {
    font-size: 1.6rem;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1rem;
    background: linear-gradient(90deg,#22d3ee,#a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Remove footer */
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================
# STATE
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"

if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

def goto_home():
    st.session_state.view = "home"
    st.rerun()

def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.rerun()

# =============================
# API
# =============================
@st.cache_data(ttl=30)
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        return r.json()
    except:
        return None

# =============================
# POSTER GRID
# =============================
def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0

    for r in range(rows):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break

            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")

            with colset[c]:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)

                if poster:
                    st.image(poster, width="stretch")
                else:
                    st.write("🖼️ No poster")

                if st.button("Open", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    goto_details(tmdb_id)

                st.markdown(
                    f'<div class="movie-title">{title}</div>',
                    unsafe_allow_html=True,
                )

                st.markdown('</div>', unsafe_allow_html=True)

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.markdown("## 🎬 Navigation")
    if st.button("🏠 Home"):
        goto_home()

    st.markdown("---")
    home_category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
    )
    grid_cols = st.slider("Grid Columns", 4, 8, 6)

# =============================
# HEADER
# =============================
st.markdown('<div class="main-title">🎬 CineVerse AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Movie Recommendation System</div>', unsafe_allow_html=True)

# ==========================================================
# HOME
# ==========================================================
if st.session_state.view == "home":

    typed = st.text_input("🔍 Search Movies", placeholder="Avengers, Batman, Love...")

    if typed.strip():
        data = api_get_json("/tmdb/search", {"query": typed.strip()})
        results = data.get("results", []) if data else []

        cards = []
        for m in results:
            cards.append(
                {
                    "tmdb_id": m.get("id"),
                    "title": m.get("title"),
                    "poster_url": f"{TMDB_IMG}{m.get('poster_path')}" if m.get("poster_path") else None,
                }
            )

        st.markdown('<div class="section-title">Search Results</div>', unsafe_allow_html=True)
        poster_grid(cards, cols=grid_cols, key_prefix="search")

    else:
        st.markdown(f'<div class="section-title">🔥 {home_category.replace("_"," ").title()}</div>', unsafe_allow_html=True)
        home_cards = api_get_json("/home", {"category": home_category, "limit": 24}) or []
        poster_grid(home_cards, cols=grid_cols, key_prefix="home")

# ==========================================================
# DETAILS
# ==========================================================
elif st.session_state.view == "details":

    tmdb_id = st.session_state.selected_tmdb_id
    data = api_get_json(f"/movie/id/{tmdb_id}")

    if not data:
        st.error("Movie not found")
        st.stop()

    col1, col2 = st.columns([1, 2.4], gap="large")

    with col1:
        st.image(data.get("poster_url"), width="stretch")

    with col2:
        st.markdown(f"## {data.get('title')}")
        st.markdown(f"**Release:** {data.get('release_date')}")
        genres = ", ".join([g["name"] for g in data.get("genres", [])])
        st.markdown(f"**Genres:** {genres}")
        st.markdown("---")
        st.write(data.get("overview"))

    if data.get("backdrop_url"):
        st.markdown('<div class="section-title">Backdrop</div>', unsafe_allow_html=True)
        st.image(data.get("backdrop_url"), width="stretch")

    st.markdown('<div class="section-title">🎯 Recommended</div>', unsafe_allow_html=True)

    bundle = api_get_json("/movie/search", {"query": data.get("title")})
    if bundle:
        poster_grid(bundle.get("genre_recommendations", []), cols=grid_cols, key_prefix="rec")

    if st.button("⬅ Back"):
        goto_home()