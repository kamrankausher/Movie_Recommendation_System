# Internship Interview Prep: Codec Technologies

## Overview
This document contains targeted interview questions based **strictly** on the bullets from your Machine Learning Internship at Codec Technologies.

### Claims Covered:
1. Python FastAPI application serving 10,000+ items on Render Cloud.
2. Latency below 150 ms via clean API design and routing.
3. Refactored data pipeline using SciPy sparse matrices.
4. Reduced memory usage vs dense implementation.
5. Modular project architecture.
6. Internal onboarding documentation.

---

## 1. FastAPI & Render Cloud Deployment
**Question:** You mentioned building a FastAPI application serving a 10,000+ item catalog on Render. Why did you choose FastAPI over Flask or Django, and how did you handle deploying such a large catalog on a cloud service?

**Ideal Answer:** 
I chose FastAPI because of its high performance, native async support, and automatic OpenAPI documentation. Serving a 45k+ item catalog required loading a large TF-IDF matrix into memory. On Render Cloud, memory is constrained, so I handled this by precomputing the similarity matrix, converting it to a SciPy Sparse CSR matrix to minimize RAM usage (dropping it to ~18MB), and loading it securely during the FastAPI `lifespan` startup event so it's ready in memory before the first request is served.

**Follow-up Question:** How did you structure the endpoints to handle both standard recommendations and TMDB-based discovery?
**Ideal Answer:** I modularized the routing using FastAPI's `APIRouter`. I separated the health checks (`/health`), TF-IDF logic (`/recommend/tfidf`), and TMDB API logic (`/tmdb/search`). This kept the API clean and maintainable.

**Common Mistake:** Discussing database optimizations (SQL/NoSQL) when the project actually uses in-memory precomputed `.pkl` files loaded at startup.

---

## 2. API Latency Optimization
**Question:** Your resume states you maintained average response latency below 150ms. How did you measure this, and what architectural decisions enabled such low latency?

**Ideal Answer:** 
I measured latency using a custom Python benchmarking script (`scripts/benchmark_latency.py`) that fired multiple consecutive requests to the endpoints and averaged the response times. To achieve sub-150ms latency (frequently under 20ms locally), I avoided calculating the TF-IDF matrix on-the-fly. Instead, the matrix is precomputed, serialized into a sparse format, and kept in memory. The endpoints only perform a fast dot-product lookup on the sparse matrix, which is highly optimized in SciPy.

**Follow-up Question:** Did the external TMDB API calls impact this 150ms target?
**Ideal Answer:** External API calls are inherently slower due to network latency, but I utilized asynchronous requests (`httpx.AsyncClient`) in FastAPI. By making non-blocking calls to TMDB, the server isn't frozen waiting for a response, ensuring concurrent users aren't bottlenecked.

**Common Mistake:** Confusing network latency (ping) with processing latency, or failing to mention `httpx` async calls.

---

## 3. SciPy Sparse Matrices & Memory Reduction
**Question:** Tell me about the refactoring of the data processing pipeline. How exactly did switching to SciPy sparse matrices reduce memory usage compared to the dense implementation?

**Ideal Answer:** 
In the original dense implementation, representing a TF-IDF matrix for 45k movies against 50k features creates a 45,000 x 50,000 NumPy array of 64-bit floats. This requires about 17 GB of RAM, which crashes typical cloud instances. However, because most movies only have a few keywords or genres, the matrix is mostly zeros. I refactored the pipeline to use a SciPy Compressed Sparse Row (CSR) matrix. The CSR matrix only stores the non-zero values and their coordinates, which reduced the memory footprint from ~17 GB down to just ~18 MB—a reduction of over 99.9%.

**Follow-up Question:** Are there performance tradeoffs when performing mathematical operations on CSR sparse matrices compared to dense matrices?
**Ideal Answer:** Yes. While sparse matrices save massive amounts of memory, operations like row slicing or adding elements can be slower than dense arrays. However, for recommendation systems, we primarily compute dot products (matrix multiplication), which CSR matrices are specifically highly optimized for.

**Common Mistake:** Not knowing the actual mathematical size difference (~17GB vs ~18MB) and just saying "it made it smaller."

---

## 4. Modular Project Architecture
**Question:** You noted applying a modular project architecture for maintainability. What did this architecture look like, and why didn't you just keep everything in a single `main.py` script?

**Ideal Answer:** 
A single `main.py` becomes a bottleneck for team collaboration and testing. I restructured the project using a standard domain-driven design:
- `app/main.py`: The application factory and entry point.
- `app/routers/`: Individual API endpoints grouped by domain (e.g., `recommend.py`, `movies.py`).
- `app/services/`: The core business logic (e.g., `recommender.py` for TF-IDF logic).
- `app/models.py`: Pydantic models for data validation.
This separation of concerns means that if we need to change how TMDB API calls are made, we only touch the services layer without risking breaking the API routing layer.

**Follow-up Question:** How did this help with testing?
**Ideal Answer:** Because the business logic was decoupled from the FastAPI routers, I could easily write isolated unit tests for the recommendation engine itself, and use FastAPI's `TestClient` to test the HTTP layer separately.

**Common Mistake:** Naming design patterns (like MVC) incorrectly. FastAPI is largely built around Routers and Services, not strict MVC.

---

## 5. Internal Onboarding Documentation
**Question:** You contributed internal onboarding documentation. What are the key elements you include in technical documentation for a new engineer joining the project?

**Ideal Answer:** 
For the `docs/onboarding.md`, I focused on minimizing the "time-to-first-commit" for new developers. The key elements included:
1. **Architecture Overview:** A simple diagram explaining how Streamlit talks to FastAPI, and FastAPI talks to the `.pkl` files and TMDB.
2. **Project Structure:** A file tree explaining where to find routes vs business logic.
3. **Local Setup Instructions:** Step-by-step commands to create the `venv`, install `requirements.txt`, setup the `.env` API keys, and run the server.
4. **API Endpoints Table:** A quick reference to the available routes.

**Follow-up Question:** How do you keep this documentation from becoming outdated?
**Ideal Answer:** By treating documentation like code—updating it in the same Pull Request that introduces structural or setup changes, and keeping it concise so it's easier to maintain.

**Common Mistake:** Assuming documentation is just a list of code comments. True onboarding documentation is about setup, architecture, and developer workflow.
