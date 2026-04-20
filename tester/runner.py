"""
tester/runner.py
Exécute tous les tests et calcule les métriques QoS :
  - latence avg + p95
  - taux d'erreur
  - disponibilité
"""

import datetime
import statistics
from tester.tests import ALL_TESTS


def run_all() -> dict:
    """
    Lance tous les tests, calcule les métriques et retourne
    un dict structuré prêt à être sauvegardé en base.
    """
    results = []

    for test_fn in ALL_TESTS:
        try:
            result = test_fn()
        except Exception as exc:
            result = {
                "name":       test_fn.__name__,
                "status":     "ERROR",
                "latency_ms": 0,
                "detail":     str(exc),
            }
        results.append(result)

    # ── Métriques ──────────────────────────────────────────
    passed  = sum(1 for r in results if r["status"] == "PASS")
    failed  = sum(1 for r in results if r["status"] == "FAIL")
    errors  = sum(1 for r in results if r["status"] == "ERROR")
    total   = len(results)

    latencies = [r["latency_ms"] for r in results if r["latency_ms"] > 0]

    avg_latency = round(statistics.mean(latencies), 2)    if latencies else 0
    p95_latency = round(
        sorted(latencies)[int(len(latencies) * 0.95) - 1], 2
    ) if len(latencies) >= 2 else (latencies[0] if latencies else 0)

    error_rate   = round((failed + errors) / total, 3) if total else 0
    availability = round(passed / total, 3)             if total else 0

    return {
        "api":       "Frankfurter",
        "timestamp": datetime.datetime.now().isoformat(),
        "summary": {
            "total":          total,
            "passed":         passed,
            "failed":         failed,
            "errors":         errors,
            "error_rate":     error_rate,
            "availability":   availability,
            "latency_ms_avg": avg_latency,
            "latency_ms_p95": p95_latency,
        },
        "tests": results,
    }