"""
Latency Benchmark: FastAPI Endpoint Response Times

Measures actual response latency for all API endpoints
by sending multiple requests and computing statistics.

Usage:
    1. Start the server: uvicorn app.main:app --port 8000
    2. Run: python scripts/benchmark_latency.py
"""

import time
import statistics
import requests

BASE_URL = "http://127.0.0.1:8000"
NUM_REQUESTS = 20


def benchmark_endpoint(method, path, params=None, label=None):
    """Send multiple requests to an endpoint and measure latency.

    Args:
        method: HTTP method ('GET' or 'POST').
        path: API endpoint path.
        params: Query parameters dict.
        label: Display label for the endpoint.

    Returns:
        Dict with min, max, avg, p95, p99 latency in ms.
    """
    url = f"{BASE_URL}{path}"
    display = label or f"{method} {path}"
    latencies = []

    for i in range(NUM_REQUESTS):
        start = time.perf_counter()
        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=30)
            else:
                response = requests.post(url, json=params, timeout=30)
            elapsed_ms = (time.perf_counter() - start) * 1000
            latencies.append(elapsed_ms)
        except Exception as exc:
            print(f"  [ERROR] Request {i+1} failed: {exc}")
            continue

    if not latencies:
        print(f"  {display}: ALL REQUESTS FAILED")
        return None

    latencies.sort()
    result = {
        "endpoint": display,
        "requests": len(latencies),
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "avg_ms": statistics.mean(latencies),
        "median_ms": statistics.median(latencies),
        "p95_ms": latencies[int(len(latencies) * 0.95)] if len(latencies) >= 20 else max(latencies),
        "status": response.status_code,
    }

    return result


def main():
    print("=" * 70)
    print("  LATENCY BENCHMARK: FastAPI Endpoint Response Times")
    print(f"  Target: {BASE_URL}")
    print(f"  Requests per endpoint: {NUM_REQUESTS}")
    print("=" * 70)

    # Verify server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
    except Exception:
        print("\n  ERROR: Server is not running at", BASE_URL)
        print("  Start it with: uvicorn app.main:app --port 8000")
        return

    endpoints = [
        ("GET", "/health", None, "GET /health"),
        ("GET", "/recommend/tfidf", {"title": "Toy Story", "top_n": 10}, "GET /recommend/tfidf (Toy Story)"),
        ("GET", "/recommend/tfidf", {"title": "Avatar", "top_n": 10}, "GET /recommend/tfidf (Avatar)"),
        ("GET", "/recommend/tfidf", {"title": "The Dark Knight", "top_n": 10}, "GET /recommend/tfidf (Dark Knight)"),
        ("GET", "/home", {"category": "popular", "limit": 10}, "GET /home (popular)"),
        ("GET", "/tmdb/search", {"query": "Batman"}, "GET /tmdb/search (Batman)"),
    ]

    results = []
    for method, path, params, label in endpoints:
        print(f"\n  Benchmarking: {label}...")
        result = benchmark_endpoint(method, path, params, label)
        if result:
            results.append(result)

    # Print results table
    print("\n" + "=" * 70)
    print("  RESULTS")
    print("=" * 70)
    print(f"  {'Endpoint':<40} {'Avg':>8} {'Min':>8} {'Max':>8} {'P95':>8} {'Status':>7}")
    print("  " + "-" * 68)

    for r in results:
        status_str = str(r["status"])
        avg = f"{r['avg_ms']:.1f}ms"
        mn = f"{r['min_ms']:.1f}ms"
        mx = f"{r['max_ms']:.1f}ms"
        p95 = f"{r['p95_ms']:.1f}ms"
        print(f"  {r['endpoint']:<40} {avg:>8} {mn:>8} {mx:>8} {p95:>8} {status_str:>7}")

    # Summary
    local_endpoints = [r for r in results if "/health" in r["endpoint"] or "/recommend/tfidf" in r["endpoint"]]
    if local_endpoints:
        avg_local = statistics.mean([r["avg_ms"] for r in local_endpoints])
        max_local = max([r["max_ms"] for r in local_endpoints])
        print(f"\n  Local endpoint average latency: {avg_local:.1f} ms")
        print(f"  Local endpoint max latency:     {max_local:.1f} ms")

        target = 150
        if avg_local < target:
            print(f"\n  [PASS] Average latency ({avg_local:.1f} ms) is below {target} ms target")
        else:
            print(f"\n  [FAIL] Average latency ({avg_local:.1f} ms) exceeds {target} ms target")

    print("=" * 70)


if __name__ == "__main__":
    main()
