# WhatsApp Task Summarizer

Aplikacja oparta o model językowy, która podsumowuje zadania z eksportów WhatsApp i prezentuje je w mobilnym interfejsie PWA. Wersja webowa działa jako SPA (React + Tailwind), a backend opiera się o FastAPI.

## Funkcje

- **Mobile-first dashboard** z kategoriami (`dom`, `firma`, `towarzyskie`) i listą zadań.
- **Upload WhatsApp TXT** i automatyczne generowanie zadań przez LLM.
- **Edycja etykiet** (kontakty + słowa kluczowe) i przypisywanie kategorii.
- **Gesty mobilne**: swipe do usuwania zadań, checkboksy ukończenia.
- **PWA**: manifest + service worker (offline cache), dark mode, share/export.
- **Autentykacja**: prosty login JWT dla wielu użytkowników.
- **WebSocket** dla aktualizacji w czasie rzeczywistym.

## Struktura projektu

```
app/                 # logika parsowania i LLM (CLI)
backend/             # FastAPI (API dla PWA)
frontend/            # React + Vite + Tailwind (SPA)
config/              # przykładowe etykiety
```

## Wymagania

- Python 3.10+
- Node.js 18+
- Klucz API OpenAI w `OPENAI_API_KEY`

## Konfiguracja środowiska

Ustaw klucz API OpenAI:

```bash
export OPENAI_API_KEY="your-key"
```

W produkcji ustaw także `SECRET_KEY` w `backend/auth.py` (docelowo w zmiennych środowiskowych).

## Uruchomienie lokalne (dev)

### Backend (FastAPI)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend startuje na `http://localhost:8000`.

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Frontend startuje na `http://localhost:5173` i komunikuje się z API pod `http://localhost:8000`.

### Demo logowanie

- **user**: `demo`
- **hasło**: `demo123`

## Build i deploy (production)

### 1) Build frontendu

```bash
cd frontend
npm install
npm run build
```

Pliki statyczne pojawią się w `frontend/dist`.

### 2) Serwowanie statyczne + API

Masz dwie opcje:

**Opcja A — serwer statyczny (np. nginx) + FastAPI:**

1. Skopiuj `frontend/dist` do serwera WWW (np. `/var/www/whatsapp-tasks`).
2. Skonfiguruj reverse proxy do FastAPI na `/api` i `/ws`.
3. Upewnij się, że aplikacja działa pod HTTPS (PWA wymaga HTTPS w produkcji).

**Opcja B — jeden serwer FastAPI (za reverse proxy):**

1. Postaw FastAPI na `gunicorn`/`uvicorn` i serwuj statyczne pliki z reverse proxy.
2. Skieruj `/` na `frontend/dist/index.html` oraz `/assets/*` na `frontend/dist/assets/*`.
3. Włącz WebSocket proxy dla `/ws/tasks`.

### 3) Konfiguracja zmiennych produkcyjnych

- `OPENAI_API_KEY`
- `SECRET_KEY` (w miejsce `change-me` w `backend/auth.py`)

## Instalacja PWA na telefonie

1. Otwórz aplikację w Safari/Chrome na telefonie.
2. Wybierz **Udostępnij** → **Dodaj do ekranu początkowego**.
3. Aplikacja działa w trybie offline (cache statyczny) i wspiera dark mode.

## Testy E2E (Cypress)

```bash
cd frontend
npm run test:e2e
```

## CLI (opcjonalne)

```bash
python -m app.main data/sample_whatsapp.txt \
  --labels config/labels.yaml \
  --model gpt-4o-mini \
  --output output.md
```
