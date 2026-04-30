# TEMA Sticky Notes

TEMA Sticky Notes is a course project exploring a sticky-notes "canvas" concept with a Python backend and supporting sprint documentation.

## Project overview & purpose

TEMA is intended to support **qualitative researchers** by providing a **canvas-based workflow** where qualitative codes can be represented as **sticky notes** that can be created, edited, and organized during thematic analysis (see sprint docs in `sprint_archive/` for full requirements and architecture).

## Tech stack

- **Backend**: Python 3, Flask 3.x (`backend/app.py`)
- **Database**: PostgreSQL 15 (development container via Docker Compose), `psycopg2-binary` (see `backend/requirements.txt`)
- **Dev tooling**: Docker / Docker Compose (`docker/development.yml`)
- **Frontend**: Electron 37 + HTML/CSS/JavaScript (`frontend/`)

## Repo layout

- **`backend/`**: Flask backend with full canvas and notes CRUD API.
  - `app.py` — Flask application with all REST endpoints.
  - `database/db.py` — `CanvasDataService` and `CodeDataService` classes for PostgreSQL access.
  - `requirements.txt` — Python dependencies.
- **`frontend/`**: Electron app with a start page and canvas view for creating, editing, dragging, and deleting sticky notes.
- **`docker/`**: Development Docker Compose config (PostgreSQL).
- **`sprint_archive/`**: Sprint PDFs (requirements, analysis, architecture, deployment).

## API endpoints

All responses include CORS headers (`Access-Control-Allow-Origin: *`).

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check — returns `{"status":"ok","message":"TEMA backend is running"}` |
| `POST` | `/api/canvases` | Create a canvas. Body: `{"name": "..."}`. Returns `{"id", "name", "message"}` (201). |
| `GET` | `/api/canvases` | List all canvases. Returns `[{"id", "name"}, ...]` (200). |
| `GET` | `/api/canvases/<canvas_id>/notes` | Get all notes for a canvas. Returns `[{"id", "collection", "text", "color", "x", "y"}, ...]` (200). |
| `POST` | `/api/canvases/<canvas_id>/notes` | Create a note. Body requires `id`; optional `collection`, `text`, `color`, `x`, `y`. Returns 201. |
| `PUT` | `/api/canvases/<canvas_id>/notes/<note_id>` | Update a note. Body accepts `text`, `color`, and/or `x`+`y`. Returns 200. |
| `DELETE` | `/api/canvases/<canvas_id>/notes/<note_id>` | Delete a note by its codeid. Returns 200. |

## Quick start

### 1) Start PostgreSQL (Docker)

```bash
docker compose -f docker/development.yml up -d
```

The compose file sets:

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

The backend starts on `http://localhost:5000`.

### 4) Run the frontend

```bash
cd frontend
npm install
npm start
```

The Electron app connects to the backend at `http://localhost:5000`.

## Team members & contributions

- **Alejandro Ciuba (PO)**: Postgres/dev environment work, DB service classes (`docker/development.yml`, `backend/database/db.py`, `backend/requirements.txt`).
- **Milan Knezevic (Dev)**: Electron UI prototype — start page and sticky-note interactions (`frontend/`).
- **Vaibhav Singh (Dev)**: Git repo setup, environment setup, integration merges into `main`, README documentation.
- **Daniel Yates (SM)**: Sprint scaffolding and integration of frontend and backend.

## Branches

- **`main`**: Full working application — Flask backend with canvas and notes CRUD, Electron frontend, Docker Postgres setup.
- **`environment_setup`**: Environment setup work (merged into `main`).
- **`db_feature`**: Initial PostgreSQL access classes (merged into `main`).
- **`feature/ui-fr1-start-page`**: Electron frontend prototype (merged into `main`).
- **`sprint4-skeleton`**: Earlier sprint skeleton branch; diverges from current `main`.

## Documentation

Sprint documentation PDFs are in `sprint_archive/`:

- `Sprint1_ Requirements Engineering.pdf`
- `Sprint2_ Analysis.pdf`
- `Sprint3_SystemArchitecture.pdf`
- `Sprint 4_ Deployment.pdf`
