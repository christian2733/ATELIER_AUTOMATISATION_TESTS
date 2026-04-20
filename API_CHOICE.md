# API Choice



- **Étudiant** : Etudiant DEV
- **API choisie** : Frankfurter (taux de change)
- **URL base** : https://api.frankfurter.app
- **Documentation officielle** : https://www.frankfurter.app/docs/
- **Auth** : None

## Endpoints testés

- `GET /latest?from=EUR`           → taux du jour depuis EUR
- `GET /latest?from=EUR&to=USD`    → taux EUR → USD uniquement
- `GET /2024-01-01?from=EUR`       → taux historique à une date
- `GET /currencies`                → liste des devises disponibles
- `GET /latest?from=INVALID`       → cas invalide (400 attendu)
- `GET /9999-99-99`                → date invalide (404 attendu)

## Hypothèses de contrat

| Champ        | Type   | Présent dans        |
|-------------|--------|---------------------|
| `amount`    | float  | /latest, /date      |
| `base`      | string | /latest, /date      |
| `date`      | string | /latest, /date      |
| `rates`     | object | /latest, /date      |
| `USD`       | float  | rates (si demandé)  |

- HTTP 200 sur tous les endpoints valides
- HTTP 400 sur devise inconnue
- HTTP 404 sur date invalide
- Content-Type: `application/json`

## Limites / rate limiting connu

- Pas de rate limit documenté officiel
- Bonne pratique : 1 run / 5 min, max 20 req/run

## Risques

- Pas disponible le week-end (marchés fermés → `rates` peut être vide)
- Légère latence selon l'heure (marchés européens)
- Pas de SLA officiel (projet open source)
