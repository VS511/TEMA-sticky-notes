from flask import Flask, jsonify, request
from services.db import CanvasDataService, CodeDataService

app = Flask(__name__)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "TEMA backend is running"}), 200


@app.route("/api/canvas", methods=["GET"])
def list_canvases():
    with CanvasDataService() as c:
        canvases = c.fetch_canvases()
    return jsonify({"canvases": canvases}), 200


@app.route("/api/canvas", methods=["POST"])
def create_canvas():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400
    with CanvasDataService() as c:
        canvas_id = c.create_canvas(name)
    return jsonify({"id": canvas_id, "name": name}), 201


@app.route("/api/canvas/<canvas_name>/note", methods=["POST"])
def add_note(canvas_name):
    data = request.get_json()
    codeid = data.get("codeid")
    text = data.get("text", "")
    color = data.get("color", 0)
    position = data.get("position", (0.0, 0.0))
    if codeid is None:
        return jsonify({"error": "codeid is required"}), 400
    with CodeDataService(canvas_name=canvas_name) as codes:
        db_id = codes.create_code_entry(
            codeid=codeid,
            text=text,
            color=color,
            position=tuple(position)
        )
    return jsonify({"id": db_id, "codeid": codeid}), 201


@app.route("/api/canvas/<canvas_name>/notes", methods=["GET"])
def get_notes(canvas_name):
    with CodeDataService(canvas_name=canvas_name) as codes:
        notes = codes.fetch_codes()
    return jsonify({"notes": notes}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)