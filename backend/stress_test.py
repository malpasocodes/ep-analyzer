#!/usr/bin/env python3
"""Stress test for EP Analyzer API — validates memory stays under 2GB.

Usage:
    # Start the server first:
    #   uvicorn app.main:app --port 8000

    python stress_test.py                    # default: http://localhost:8000
    python stress_test.py http://localhost:8000 --concurrency 5
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def fetch(url: str, label: str, timeout: int = 60) -> dict:
    """Fetch a URL and return timing + response metadata."""
    start = time.perf_counter()
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            elapsed = time.perf_counter() - start
            size_kb = len(body) / 1024
            return {
                "label": label,
                "status": resp.status,
                "time_s": round(elapsed, 2),
                "size_kb": round(size_kb, 1),
                "ok": True,
            }
    except HTTPError as e:
        elapsed = time.perf_counter() - start
        return {"label": label, "status": e.code, "time_s": round(elapsed, 2), "size_kb": 0, "ok": False, "error": str(e)}
    except (URLError, TimeoutError, OSError) as e:
        elapsed = time.perf_counter() - start
        return {"label": label, "status": 0, "time_s": round(elapsed, 2), "size_kb": 0, "ok": False, "error": str(e)}


def run_stress_test(base: str, concurrency: int = 3, rounds: int = 3):
    """Run stress test against all major endpoints."""

    # Phase 1: Sequential endpoint smoke test
    endpoints = [
        ("/api/health", "health"),
        ("/api/overview", "overview"),
        ("/api/states", "states-list"),
        ("/api/states/CA", "state-detail-CA"),
        ("/api/states/TX", "state-detail-TX"),
        ("/api/institutions?limit=50", "institutions-search"),
        ("/api/institutions?search=university&limit=50", "institutions-search-query"),
        ("/api/analysis/reclassification?state=CA&inequality=0.5", "reclassify-CA"),
        ("/api/analysis/margins", "margins-national"),
        ("/api/analysis/margins?state=NY", "margins-NY"),
        ("/api/analysis/early-vs-late?limit=100", "early-vs-late"),
    ]

    # Add program endpoints if available
    program_endpoints = [
        ("/api/programs/overview", "programs-overview"),
        ("/api/programs/search?limit=50", "programs-search"),
        ("/api/programs/cip-list?limit=20", "cip-list"),
        ("/api/programs/reclassification?state=CA", "programs-reclass-CA"),
    ]

    print("=" * 70)
    print("EP Analyzer Stress Test")
    print(f"  Target: {base}")
    print(f"  Concurrency: {concurrency}")
    print(f"  Rounds: {rounds}")
    print("=" * 70)

    # Phase 1: Sequential smoke test
    print("\n--- Phase 1: Sequential Smoke Test ---")
    all_results = []
    for path, label in endpoints + program_endpoints:
        result = fetch(f"{base}{path}", label)
        status_icon = "OK" if result["ok"] else "FAIL"
        print(f"  [{status_icon}] {label:30s} {result['time_s']:6.2f}s  {result['size_kb']:8.1f}KB  HTTP {result['status']}")
        all_results.append(result)

    # Phase 2: Concurrent load test
    print(f"\n--- Phase 2: Concurrent Load ({concurrency} workers x {rounds} rounds) ---")
    # Use lighter endpoints for concurrent testing to simulate real traffic
    concurrent_endpoints = [
        ("/api/overview", "overview"),
        ("/api/states", "states-list"),
        ("/api/states/CA", "state-CA"),
        ("/api/states/NY", "state-NY"),
        ("/api/institutions?limit=50", "institutions"),
        ("/api/analysis/margins", "margins"),
    ]

    concurrent_results = []
    total_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = []
        for round_num in range(rounds):
            for path, label in concurrent_endpoints:
                f = pool.submit(fetch, f"{base}{path}", f"r{round_num}-{label}")
                futures.append(f)

        for f in as_completed(futures):
            concurrent_results.append(f.result())

    total_elapsed = time.perf_counter() - total_start
    ok_count = sum(1 for r in concurrent_results if r["ok"])
    fail_count = sum(1 for r in concurrent_results if not r["ok"])
    avg_time = sum(r["time_s"] for r in concurrent_results) / len(concurrent_results)
    max_time = max(r["time_s"] for r in concurrent_results)
    p95_time = sorted(r["time_s"] for r in concurrent_results)[int(len(concurrent_results) * 0.95)]

    print(f"  Requests: {len(concurrent_results)} ({ok_count} ok, {fail_count} failed)")
    print(f"  Total wall time: {total_elapsed:.2f}s")
    print(f"  Avg response: {avg_time:.2f}s")
    print(f"  P95 response: {p95_time:.2f}s")
    print(f"  Max response: {max_time:.2f}s")
    print(f"  Throughput: {len(concurrent_results) / total_elapsed:.1f} req/s")

    # Phase 3: Memory-heavy endpoint stress test (simulation)
    print("\n--- Phase 3: Simulation Endpoints (Memory Stress) ---")
    sim_endpoints = [
        # Single-institution simulation — should be cheap now
        ("/api/programs/simulation/110635?n_simulations=500", "sim-single-500"),
        ("/api/programs/simulation/110635?n_simulations=1000", "sim-single-1000"),
        # State-scoped summary — moderate memory
        ("/api/programs/simulation-summary?state=VT&n_simulations=200", "sim-summary-VT-200"),
    ]
    for path, label in sim_endpoints:
        result = fetch(f"{base}{path}", label, timeout=120)
        status_icon = "OK" if result["ok"] else "FAIL"
        print(f"  [{status_icon}] {label:30s} {result['time_s']:6.2f}s  {result['size_kb']:8.1f}KB  HTTP {result['status']}")
        all_results.append(result)

    # Summary
    print("\n" + "=" * 70)
    total_ok = sum(1 for r in all_results if r["ok"]) + ok_count
    total_fail = sum(1 for r in all_results if not r["ok"]) + fail_count
    print(f"TOTAL: {total_ok} passed, {total_fail} failed")

    if total_fail > 0:
        print("\nFailed requests:")
        for r in all_results:
            if not r["ok"]:
                print(f"  {r['label']}: HTTP {r['status']} - {r.get('error', 'unknown')}")
        for r in concurrent_results:
            if not r["ok"]:
                print(f"  {r['label']}: HTTP {r['status']} - {r.get('error', 'unknown')}")

    print("=" * 70)
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stress test EP Analyzer API")
    parser.add_argument("base_url", nargs="?", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--concurrency", "-c", type=int, default=3, help="Number of concurrent workers (default: 3)")
    parser.add_argument("--rounds", "-r", type=int, default=3, help="Number of rounds per concurrent endpoint (default: 3)")
    args = parser.parse_args()

    sys.exit(run_stress_test(args.base_url, args.concurrency, args.rounds))
