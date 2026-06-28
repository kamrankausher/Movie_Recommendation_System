"""
Memory Benchmark: Sparse vs Dense TF-IDF Matrix

Compares memory usage between the SciPy sparse CSR matrix
and its equivalent dense NumPy array. Demonstrates the
efficiency gain from using sparse matrices.

Usage:
    python scripts/benchmark_memory.py
"""

import os
import sys
import pickle
import time

import numpy as np
import scipy.sparse

# Path to the pickle file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TFIDF_MATRIX_PATH = os.path.join(BASE_DIR, "data", "tfidf_matrix.pkl")


def format_bytes(size_bytes):
    """Convert bytes to a human-readable string."""
    if size_bytes >= 1024 ** 3:
        return f"{size_bytes / (1024 ** 3):.2f} GB"
    if size_bytes >= 1024 ** 2:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes} B"


def main():
    print("=" * 60)
    print("  MEMORY BENCHMARK: Sparse vs Dense TF-IDF Matrix")
    print("=" * 60)

    # Load sparse matrix
    print("\n[1] Loading sparse matrix from tfidf_matrix.pkl...")
    with open(TFIDF_MATRIX_PATH, "rb") as f:
        sparse_matrix = pickle.load(f)

    print(f"    Type:  {type(sparse_matrix).__name__}")
    print(f"    Shape: {sparse_matrix.shape}")
    print(f"    Non-zero elements: {sparse_matrix.nnz:,}")
    sparsity = (1 - sparse_matrix.nnz / (sparse_matrix.shape[0] * sparse_matrix.shape[1])) * 100
    print(f"    Sparsity: {sparsity:.2f}%")

    # Measure sparse memory
    sparse_bytes = (
        sparse_matrix.data.nbytes
        + sparse_matrix.indices.nbytes
        + sparse_matrix.indptr.nbytes
    )
    print(f"\n[2] SPARSE matrix memory: {format_bytes(sparse_bytes)}")

    # Calculate dense memory (without actually allocating it)
    rows, cols = sparse_matrix.shape
    dense_bytes = rows * cols * 8  # float64 = 8 bytes
    print(f"    DENSE  matrix memory: {format_bytes(dense_bytes)} (calculated)")

    # Memory reduction
    reduction = (1 - sparse_bytes / dense_bytes) * 100
    ratio = dense_bytes / sparse_bytes

    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(f"  Sparse memory:     {format_bytes(sparse_bytes)}")
    print(f"  Dense memory:      {format_bytes(dense_bytes)}")
    print(f"  Memory reduction:  {reduction:.1f}%")
    print(f"  Compression ratio: {ratio:.0f}x smaller")
    print("=" * 60)

    # Speed benchmark: sparse vs dense similarity computation
    print("\n[3] Speed benchmark: cosine similarity computation...")

    # Sparse multiplication
    query_vec = sparse_matrix[0]
    start = time.perf_counter()
    for _ in range(10):
        _ = (sparse_matrix @ query_vec.T).toarray().ravel()
    sparse_time = (time.perf_counter() - start) / 10

    print(f"    Sparse similarity (avg of 10 runs): {sparse_time * 1000:.1f} ms")

    # Dense multiplication (only on a small slice to avoid OOM)
    sample_size = min(5000, rows)
    dense_sample = sparse_matrix[:sample_size].toarray()
    query_dense = dense_sample[0]

    start = time.perf_counter()
    for _ in range(10):
        _ = (dense_sample @ query_dense.T).ravel()
    dense_time = (time.perf_counter() - start) / 10

    print(f"    Dense  similarity (avg of 10, {sample_size} rows): {dense_time * 1000:.1f} ms")

    print("\n" + "=" * 60)
    print("  CONCLUSION")
    print("=" * 60)
    print(f"  Using SciPy sparse matrices reduces memory by {reduction:.1f}%")
    print(f"  ({format_bytes(dense_bytes)} -> {format_bytes(sparse_bytes)})")
    print(f"  This is a {ratio:.0f}x compression ratio.")
    print("=" * 60)


if __name__ == "__main__":
    main()
