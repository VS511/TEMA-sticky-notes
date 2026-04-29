# TEMA Sticky Notes

TEMA Sticky Notes is a course project exploring a sticky-notes “canvas” concept with a Python backend and supporting sprint documentation.

## Project overview & purpose

TEMA is intended to support **qualitative researchers** by providing a **canvas-based workflow** where qualitative codes can be represented as **sticky notes** that can be created, edited, and organized during thematic analysis (see sprint docs in `doc/` for full requirements and architecture).

## Tech stack (current + in-progress branches)

- **Backend**: Python, Flask (`backend/app.py`)
- **Database**: PostgreSQL (development container via Docker Compose), `psycopg2` (see `requirements/python-requirements.txt`)
- **Dev tooling**: Docker / Docker Compose (`docker/development.yml`)
- **Frontend (branch work)**: Electron + HTML/CSS/JavaScript (`feature/ui-fr1-start-page` branch)

## Repo layout

- `**backend/`**: Flask backend (currently includes a health check endpoint).
- `**docker/**`: Development Docker config (PostgreSQL).
- `**sprint_archive/**`: Sprint PDFs (requirements, analysis, architecture).

## Implemented features (so far)

- **Backend health endpoint**
  - **What it does**: Confirms the Flask backend is running.
  - **How to use**: Run the backend, then request `GET /api/health`. Expected response:
    - `{"status":"ok","message":"TEMA backend is running"}`
- **Development PostgreSQL via Docker Compose**
  - **What it does**: Starts a local Postgres instance for development.
  - **How to use**: Run the compose command shown below, then connect using the credentials in `docker/development.yml`.
- **Canvas persistence scaffolding (branch: `db_feature`)**
  - **What it does**: Adds initial DB access classes and a `canvas` table creator plus basic create/fetch APIs.
  - **How to use**: Check out `origin/db_feature`, start Postgres, then run `python backend/services/db.py` to exercise the demo `create_canvas()` / `fetch_canvases()` calls.
- **Start page + draggable sticky notes (branch: `feature/ui-fr1-start-page`)**
  - **What it does**: Adds an Electron prototype UI with a start page and a canvas screen where sticky notes can be added and dragged.
  - **How to use**: Check out `origin/feature/ui-fr1-start-page`, then from `frontend/` run:
    - `npm install`
    - `npm start`

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
pip install -r backend/requirements.txt
```

### 3) Run the backend

```bash
python backend/app.py
```

Then verify:

- `GET /api/health` → `{"status":"ok","message":"TEMA backend is running"}`

## Team members & contributions

Team and sprint roles (from `doc/` PDFs):

- **Alejandro Ciuba (PO)**: Authored Postgres/dev environment work and DB service work (`docker/development.yml`, `requirements/python-requirements.txt` updates, `db_feature` branch).
- **Milan Knezevic (Dev)**: Implemented the initial UI prototype work on the Electron start page / sticky-note interactions (e.g., `feature/ui-fr1-start-page` branch).
- **Vaibhav Singh (Dev)**: Git repo setup, environment setup integration and merges into`main`. Authored [README.md](http://README.md) documentation.
- **Daniel Yates (SM)**: Sprint skeleton / scaffolding contributions and integration of frontend and backend.

## Branches

This repo has several branches that represent different work streams:

- `**main`**: Baseline backend + docker Postgres setup (and merges from earlier sprint skeleton / environment setup work).
- `**environment_setup**`: Environment setup work that is merged into `main`.
- `**db_feature**`: Adds `backend/services/db.py` with initial PostgreSQL access classes (uses `psycopg2` and the dev DB credentials in the compose file).
- `**feature/ui-fr1-start-page**`: Adds an Electron frontend (`frontend/`) with a start page and a basic draggable sticky note interaction.
- `**sprint4-skeleton**`: Earlier sprint skeleton branch; note it diverges from current `main` and does not include the current docker/requirements files as-is.

## Documentation

Sprint documentation PDFs are in `doc/`:

- `Sprint1_ Requirements Engineering.pdf`
- `Sprint2_ Analysis.pdf`
- `Sprint3_SystemArchitecture.pdf`
- `Sprint4_Deployment.pdf`

