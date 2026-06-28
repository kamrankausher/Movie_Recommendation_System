FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and data files
COPY app/ ./app/
COPY df.pkl .
COPY tfidf_matrix.pkl .
COPY tfidf.pkl .
COPY indices.pkl .
COPY .env .

EXPOSE 10000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
