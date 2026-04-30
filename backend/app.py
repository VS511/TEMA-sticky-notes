import os

from flask import Flask, jsonify, make_response, request, send_from_directory
from psycopg2 import IntegrityError

from database.db import CanvasDataService, CodeDataService

_COLLECTION_MAX_LEN = 100


def _normalize_collection(value):
    if not isinstance(value, str):
        return None, ({"error": "collection must be a string"}, 400)
    trimmed = value.strip()
    if not trimmed:
        return None, ({"error": "collection cannot be empty"}, 400)
    if len(trimmed) > _COLLECTION_MAX_LEN:
        return None, ({"error": f"collection must be at most {_COLLECTION_MAX_LEN} characters"}, 400)
    return trimmed, None

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_BACKEND_DIR)
_FRONTEND_DIR = os.path.join(_REPO_ROOT, "frontend")

app = Flask(__name__)


#canvas routes

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response


@app.route("/", methods=["GET"])
def serve_frontend():
    """Serve UI over HTTP so the page and /api/* share one origin (fixes broken fetch from file:// or port/host mismatch)."""
    response = make_response(send_from_directory(_FRONTEND_DIR, "index.html"))
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "TEMA backend is running"}), 200


@app.route("/api/canvases", methods=["POST"])
def create_canvas():
    data = request.get_json(silent=True)

    if not data or "name" not in data:
        return jsonify({"error": "Canvas name is required"}), 400

    canvas_name = (data.get("name") or "").strip()
    if not canvas_name:
        return jsonify({"error": "Canvas name is required"}), 400

    try:
        with CanvasDataService() as canvas_service:
            canvas_id = canvas_service.create_canvas(canvas_name)

        return jsonify(
            {
                "id": canvas_id,
                "name": canvas_name,
                "message": "Canvas created successfully",
            }
        ), 201

    except IntegrityError:
        return jsonify(
            {"error": "A canvas with that name already exists. Pick a different name or open it from the list."}
        ), 409
    except Exception as error:
        print("[TEMA] create_canvas failed:", repr(error))
        return jsonify({"error": str(error)}), 500
    

@app.route("/api/canvases", methods=["GET"])
def get_canvases():
    try:
        with CanvasDataService() as canvas_service:
            canvases = canvas_service.fetch_canvases()

        canvas_list = [
            {"id": canvas[0], "name": canvas[1]}
            for canvas in canvases
        ]

        return jsonify(canvas_list), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500
    


#sticky notes routes

@app.route("/api/canvases/<int:canvas_id>/notes", methods=["GET"])
def get_notes(canvas_id):
    table_name = f"canvas_{canvas_id}"

    try:
        with CodeDataService(canvas_name=table_name) as code_service:
            rows = code_service.fetch_codes()

        notes = []

        for row in rows:
            position = row[5]

            # PostgreSQL POINT may come back like "(40,50)"
            x = 40
            y = 40

            if position is not None:
                position_string = str(position).replace("(", "").replace(")", "")
                parts = position_string.split(",")

                if len(parts) == 2:
                    x = float(parts[0])
                    y = float(parts[1])

            notes.append({
                "id": row[1],          # codeid
                "collection": row[2],
                "text": row[3],
                "color": row[4],
                "x": x,
                "y": y
            })

        return jsonify(notes), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/canvases/<int:canvas_id>/groups", methods=["GET"])
def get_groups(canvas_id):
    table_name = f"canvas_{canvas_id}"

    try:
        with CodeDataService(canvas_name=table_name) as code_service:
            rows = code_service.get_collection_counts()

        groups = [{"name": name, "count": count} for name, count in rows]
        return jsonify(groups), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/canvases/<int:canvas_id>/notes", methods=["POST"])
def create_note(canvas_id):
    table_name = f"canvas_{canvas_id}"
    data = request.get_json(silent=True)

    if not data or "id" not in data:
        return jsonify({"error": "Note id is required"}), 400

    collection = "default"
    if "collection" in data:
        coll, err = _normalize_collection(data["collection"])
        if err:
            return jsonify(err[0]), err[1]
        collection = coll

    try:
        note_data = {
            "codeid": data["id"],
            "collection": collection,
            "text": data.get("text", ""),
            "color": data.get("color", 0),
            "position": (
                float(data.get("x", 40)),
                float(data.get("y", 40))
            )
        }

        with CodeDataService(canvas_name=table_name) as code_service:
            database_id = code_service.create_code_entry(**note_data)

        return jsonify({
            "database_id": database_id,
            "id": data["id"],
            "message": "Note created successfully"
        }), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/canvases/<int:canvas_id>/notes/<int:note_id>", methods=["PUT"])
def update_note(canvas_id, note_id):
    table_name = f"canvas_{canvas_id}"
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Note data is required"}), 400

    try:
        note_data = {
            "codeid": note_id
        }

        if "text" in data:
            note_data["text"] = data["text"]

        if "color" in data:
            note_data["color"] = data["color"]

        if "x" in data and "y" in data:
            note_data["position"] = (
                float(data["x"]),
                float(data["y"])
            )

        if "collection" in data:
            coll, err = _normalize_collection(data["collection"])
            if err:
                return jsonify(err[0]), err[1]
            note_data["collection"] = coll

        with CodeDataService(canvas_name=table_name) as code_service:
            code_service.update_code_entry(**note_data)

        return jsonify({
            "id": note_id,
            "message": "Note updated successfully"
        }), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500

@app.route("/api/canvases/<int:canvas_id>/notes/<int:note_id>", methods=["DELETE"])
def delete_note(canvas_id, note_id):
    table_name = f"canvas_{canvas_id}"
    try:
        with CodeDataService(canvas_name=table_name) as code_service:
            code_service.delete_code_entry(codeid=note_id)
        return jsonify({"message": "Note deleted successfully"}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

if __name__ == "__main__":
    # Team default is 5000; allow local override on blocked machines.
    port = int(os.environ.get("TEMA_PORT", "5000"))
    app.run(debug=True, host="127.0.0.1", port=port)

    
