#!/usr/bin/env python3
"""
cron_run.py
Script à planifier sur PythonAnywhere (Scheduled Task).
Déclenche un run de tests et sauvegarde le résultat en base.

Configuration PythonAnywhere :
  Commande : python /home/<user>/api-tester/cron_run.py
  Fréquence : toutes les heures (ou toutes les 5 min en compte payant)
"""

import sys
import os

# Ajoute le répertoire du projet dans le path
sys.path.insert(0, os.path.dirname(__file__))

from tester.runner import run_all
from storage import init_db, save_run
import json

def main():
    init_db()
    print("Lancement du run de tests...")
    result = run_all()
    save_run(result)

    s = result["summary"]
    print(f"✅ Run terminé : {s['passed']}/{s['total']} passés "
          f"| avg={s['latency_ms_avg']}ms "
          f"| p95={s['latency_ms_p95']}ms "
          f"| erreur={s['error_rate']*100:.1f}%")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()