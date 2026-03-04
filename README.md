# pkp-bet monorepo

Monorepo aplikacji **PKP Bet**:
- Backend: FastAPI + PostgreSQL
- Frontend: Next.js
- Orkiestracja: docker-compose

## Funkcje

Backend:
- klient PKP PLK (`pdp-api.plk-sa.pl`) z nagłówkiem `X-API-Key`
- job co 2 min pobiera:
  - `GET /api/v1/operations?carriersInclude=IC&withPlanned=true`
- zapis snapshotów do tabeli `run_updates`
- endpointy:
  - `GET /runs/today`
  - `GET /runs/{id}`
  - `POST /bets`
  - `GET /leaderboard`
- modele/tabele:
  - `stations`
  - `train_runs`
  - `run_updates`
  - `users`
  - `bets`
  - `ledger`

Frontend:
- lista dzisiejszych pociągów IC z opóźnieniem live (polling)
- ekran „obstaw” (slider minut + stawka)
- ranking

## Uruchomienie lokalne

1. Skopiuj przykładowy env:

```bash
cp .env.example .env
```

2. Wklej klucz PKP PLK do `.env`:

```env
PLK_API_KEY=tu_wklej_swoj_klucz
```

3. Uruchom stack:

```bash
docker compose up --build
```

4. Otwórz:
- Frontend: http://localhost:3000
- Backend OpenAPI: http://localhost:8000/docs

## Notatki
- Backend seeduje użytkowników startowych: `alice`, `bob`, `charlie`.
- Bez poprawnego `PLK_API_KEY` lista pociągów może pozostać pusta.
