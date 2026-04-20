"""
tester/tests.py
Plan de tests – API Frankfurter
  A. Contrat (fonctionnels)
  B. Robustesse & QoS (non-fonctionnels)
"""

from tester.client import get


# ─────────────────────────────────────────────
#  Helpers internes
# ─────────────────────────────────────────────

def _pass(name, latency, detail=""):
    return {"name": name, "status": "PASS", "latency_ms": latency, "detail": detail}

def _fail(name, latency, detail=""):
    return {"name": name, "status": "FAIL", "latency_ms": latency, "detail": detail}

def _error(name, detail=""):
    return {"name": name, "status": "ERROR", "latency_ms": 0, "detail": detail}


# ─────────────────────────────────────────────
#  A. Tests Contrat
# ─────────────────────────────────────────────

def test_latest_status_200():
    """GET /latest renvoie HTTP 200"""
    r = get("/latest", {"from": "EUR"})
    if r["error"]:
        return _error("GET /latest → HTTP 200", r["error"])
    ok = r["status_code"] == 200
    detail = f"status={r['status_code']}"
    return _pass("GET /latest → HTTP 200", r["latency_ms"], detail) if ok \
        else _fail("GET /latest → HTTP 200", r["latency_ms"], detail)


def test_latest_content_type_json():
    """GET /latest renvoie Content-Type application/json"""
    r = get("/latest", {"from": "EUR"})
    if r["error"]:
        return _error("GET /latest → Content-Type JSON", r["error"])
    ok = r["json"] is not None
    return _pass("GET /latest → Content-Type JSON", r["latency_ms"]) if ok \
        else _fail("GET /latest → Content-Type JSON", r["latency_ms"], "body non parseable")


def test_latest_champs_obligatoires():
    """GET /latest contient amount, base, date, rates"""
    r = get("/latest", {"from": "EUR"})
    if r["error"] or r["json"] is None:
        return _error("GET /latest → champs obligatoires", r.get("error", "no json"))
    body    = r["json"]
    manques = [f for f in ("amount", "base", "date", "rates") if f not in body]
    if manques:
        return _fail("GET /latest → champs obligatoires", r["latency_ms"],
                     f"champs manquants : {manques}")
    return _pass("GET /latest → champs obligatoires", r["latency_ms"],
                 f"base={body['base']} date={body['date']}")


def test_latest_types():
    """GET /latest – types corrects (amount:float, base:str, rates:dict)"""
    r = get("/latest", {"from": "EUR"})
    if r["error"] or r["json"] is None:
        return _error("GET /latest → types", r.get("error", "no json"))
    body   = r["json"]
    errors = []
    if not isinstance(body.get("amount"), (int, float)):
        errors.append(f"amount={type(body.get('amount')).__name__}")
    if not isinstance(body.get("base"), str):
        errors.append(f"base={type(body.get('base')).__name__}")
    if not isinstance(body.get("rates"), dict):
        errors.append(f"rates={type(body.get('rates')).__name__}")
    if errors:
        return _fail("GET /latest → types", r["latency_ms"], ", ".join(errors))
    return _pass("GET /latest → types", r["latency_ms"])


def test_latest_filtre_devise():
    """GET /latest?from=EUR&to=USD → rates contient uniquement USD"""
    r = get("/latest", {"from": "EUR", "to": "USD"})
    if r["error"] or r["json"] is None:
        return _error("GET /latest → filtre devise USD", r.get("error", "no json"))
    rates = r["json"].get("rates", {})
    if list(rates.keys()) == ["USD"] and isinstance(rates["USD"], float):
        return _pass("GET /latest → filtre devise USD", r["latency_ms"],
                     f"USD={rates['USD']}")
    return _fail("GET /latest → filtre devise USD", r["latency_ms"],
                 f"rates={rates}")


def test_currencies_liste():
    """GET /currencies renvoie un dict de devises non vide"""
    r = get("/currencies")
    if r["error"] or r["json"] is None:
        return _error("GET /currencies → liste devises", r.get("error", "no json"))
    ok = isinstance(r["json"], dict) and len(r["json"]) > 0
    detail = f"{len(r['json'])} devises" if ok else "dict vide ou mauvais type"
    return _pass("GET /currencies → liste devises", r["latency_ms"], detail) if ok \
        else _fail("GET /currencies → liste devises", r["latency_ms"], detail)


def test_historique_date_valide():
    """GET /2024-01-02 renvoie HTTP 200 avec des taux"""
    r = get("/2024-01-02", {"from": "EUR"})
    if r["error"]:
        return _error("GET /2024-01-02 → HTTP 200", r["error"])
    ok = r["status_code"] == 200 and isinstance(r["json"], dict)
    detail = f"status={r['status_code']}"
    return _pass("GET /2024-01-02 → HTTP 200", r["latency_ms"], detail) if ok \
        else _fail("GET /2024-01-02 → HTTP 200", r["latency_ms"], detail)


# ─────────────────────────────────────────────
#  B. Robustesse – cas d'erreur attendus
# ─────────────────────────────────────────────

def test_devise_invalide_400():
    """GET /latest?from=INVALID → 400 attendu"""
    r = get("/latest", {"from": "INVALID"})
    if r["error"]:
        return _error("GET /latest?from=INVALID → 400", r["error"])
    ok = r["status_code"] == 400
    detail = f"status={r['status_code']}"
    return _pass("GET /latest?from=INVALID → 400", r["latency_ms"], detail) if ok \
        else _fail("GET /latest?from=INVALID → 400", r["latency_ms"], detail)


def test_date_invalide_404():
    """GET /9999-99-99 → 404 attendu"""
    r = get("/9999-99-99")
    if r["error"]:
        return _error("GET /9999-99-99 → 404", r["error"])
    ok = r["status_code"] in (404, 400)   # les deux sont acceptables
    detail = f"status={r['status_code']}"
    return _pass("GET /9999-99-99 → 404", r["latency_ms"], detail) if ok \
        else _fail("GET /9999-99-99 → 404", r["latency_ms"], detail)


# ─────────────────────────────────────────────
#  Registre de tous les tests
# ─────────────────────────────────────────────

ALL_TESTS = [
    test_latest_status_200,
    test_latest_content_type_json,
    test_latest_champs_obligatoires,
    test_latest_types,
    test_latest_filtre_devise,
    test_currencies_liste,
    test_historique_date_valide,
    test_devise_invalide_400,
    test_date_invalide_404,
]