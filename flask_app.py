"""
flask_app.py
Application Flask – API Tester Dashboard
Routes :
  GET  /           → redirige vers /dashboard
  POST /run        → déclenche un run de tests
  GET  /dashboard  → tableau de bord + historique
  GET  /run/<id>   → détail d'un run
  GET  /health     → état de santé de la solution [BONUS]
  GET  /export     → export JSON de tous les runs [BONUS]
"""

import json
from flask import Flask, redirect, render_template, jsonify, url_for

from tester.runner import run_all
from storage import init_db, save_run, list_runs, get_run

app = Flask(__name__)
init_db()


# ── Accueil ───────────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("dashboard"))


# ── Déclenchement d'un run ────────────────────────────────
@app.route("/run", methods=["GET", "POST"])
def run():
    result = run_all()
    save_run(result)
    return jsonify(result)


# ── Dashboard ─────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    runs = list_runs(limit=20)

    # Dernier run pour la synthèse en haut de page
    last = runs[0] if runs else None

    # Tendance latence pour le mini-graphe (10 derniers runs, ordre chronologique)
    trend = list(reversed([
        {
            "ts":  r["timestamp"][:16].replace("T", " "),
            "avg": r["latency_avg"],
            "p95": r["latency_p95"],
        }
        for r in runs[:10]
    ]))

    return render_template("dashboard.html",
                           runs=runs,
                           last=last,
                           trend=json.dumps(trend))


# ── Détail d'un run ───────────────────────────────────────
@app.route("/run/<int:run_id>")
def run_detail(run_id):
    r = get_run(run_id)
    if r is None:
        return "Run introuvable", 404
    return render_template("run_detail.html", run=r)


# ── Health check [BONUS] ──────────────────────────────────
@app.route("/health")
def health():
    runs = list_runs(limit=1)
    if not runs:
        return jsonify({"status": "no_data", "message": "Aucun run effectué"}), 200

    last = runs[0]
    status = "ok" if last["availability"] >= 0.8 else "degraded"
    return jsonify({
        "status":       status,
        "last_run":     last["timestamp"],
        "availability": last["availability"],
        "error_rate":   last["error_rate"],
        "latency_avg":  last["latency_avg"],
    })


# ── Export JSON [BONUS] ───────────────────────────────────
@app.route("/export")
def export():
    runs = list_runs(limit=100)
    return jsonify(runs), 200, {
        "Content-Disposition": "attachment; filename=runs_export.json"
    }


if __name__ == "__main__":
    app.run(debug=True)
