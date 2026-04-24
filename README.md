# TEMA Sticky Notes

TEMA Sticky Notes is a course project exploring a sticky-notes “canvas” concept with a Python backend and supporting sprint documentation.

## Repo layout

- **`backend/`**: Flask backend (currently includes a health check endpoint).
- **`docker/`**: Development Docker config (PostgreSQL).
- **`requirements/`**: Dependency lists (Python).
- **`doc/`**: Sprint PDFs (requirements, analysis, architecture).
- **`src/`**: Placeholder directory (currently empty on `main`).

## Quick start (current `main`)

### 1) Start PostgreSQL (Docker)

The repo includes a compose file at `docker/development.yml` that starts a Postgres container.

From the repo root:

```bash
docker compose -f docker/development.yml up -d
```

The compose file currently sets:
- **user**: `dev`
- **password**: `12345`
- **db**: `dev_db`
- **port**: `5432`

### 2) Install backend dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/python-requirements.txt
```

### 3) Run the backend

```bash
python backend/app.py
```

Then verify:

- `GET /api/health` → `{"status":"ok","message":"TEMA backend is running"}`

## Branches

This repo has several branches that represent different work streams:

- **`main`**: Baseline backend + docker Postgres setup (and merges from earlier sprint skeleton / environment setup work).
- **`environment_setup`**: Environment setup work that is merged into `main`.
- **`db_feature`**: Adds `backend/services/db.py` with initial PostgreSQL access classes (uses `psycopg2` and the dev DB credentials in the compose file).
- **`feature/ui-fr1-start-page`**: Adds an Electron frontend (`frontend/`) with a start page and a basic draggable sticky note interaction.
- **`sprint4-skeleton`**: Earlier sprint skeleton branch; note it diverges from current `main` and does not include the current docker/requirements files as-is.

## Documentation

Sprint documentation PDFs are in `doc/`:

- `Sprint1_ Requirements Engineering.pdf`
- `Sprint2_ Analysis.pdf`
- `Sprint3_SystemArchitecture.pdf`

