"""
tester/client.py
Wrapper HTTP : timeout, retry, mesure de latence, gestion 429/5xx
"""

import time
import requests

BASE_URL = "https://api.frankfurter.app"
TIMEOUT  = 3          # secondes
MAX_RETRY = 1         # 1 seul retry max


def get(path: str, params: dict = None) -> dict:
    """
    Effectue un GET sur BASE_URL + path.
    Retourne un dict avec :
        - status_code  (int)
        - json         (dict | None)
        - latency_ms   (float)
        - error        (str | None)
        - retried      (bool)
    """
    url     = BASE_URL + path
    retried = False

    for attempt in range(MAX_RETRY + 1):
        try:
            start    = time.perf_counter()
            response = requests.get(url, params=params, timeout=TIMEOUT)
            latency  = (time.perf_counter() - start) * 1000  # → ms

            # Gestion 429 : on attend et on retente une fois
            if response.status_code == 429 and attempt < MAX_RETRY:
                retried = True
                retry_after = int(response.headers.get("Retry-After", 2))
                time.sleep(retry_after)
                continue

            # Gestion 5xx : retry immédiat une fois
            if response.status_code >= 500 and attempt < MAX_RETRY:
                retried = True
                time.sleep(1)
                continue

            # Lecture JSON (peut être None si réponse non-JSON)
            try:
                body = response.json()
            except Exception:
                body = None

            return {
                "status_code": response.status_code,
                "json":        body,
                "latency_ms":  round(latency, 2),
                "error":       None,
                "retried":     retried,
            }

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRY:
                retried = True
                continue
            return {
                "status_code": None,
                "json":        None,
                "latency_ms":  TIMEOUT * 1000,
                "error":       "TIMEOUT",
                "retried":     retried,
            }

        except requests.exceptions.RequestException as exc:
            return {
                "status_code": None,
                "json":        None,
                "latency_ms":  0,
                "error":       str(exc),
                "retried":     retried,
            }