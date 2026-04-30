from flask import Flask, jsonify, request
from database.db import CanvasDataService, CodeDataService

app = Flask(__name__)


#canvas routes

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "TEMA backend is running"}), 200


@app.route("/api/canvases", methods=["POST"])
def create_canvas():
    data = request.get_json(silent=True)

    if not data or "name" not in data:
        return jsonify({"error": "Canvas name is required"}), 400
    
    canvas_name = data["name"]

    try:
        with CanvasDataService() as canvas_service:
            canvas_id = canvas_service.create_canvas(canvas_name)

        return jsonify({
            "id": canvas_id,
            "name": canvas_name,
            "message": "Canvas created successfully"
        }), 201
    
    except Exception as error:
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
                "y": y,
                "backgroundColor": row[6],
                "borderColor": row[7]
            })

        return jsonify(notes), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/canvases/<int:canvas_id>/notes", methods=["POST"])
def create_note(canvas_id):
    table_name = f"canvas_{canvas_id}"
    data = request.get_json(silent=True)

    if not data or "id" not in data:
        return jsonify({"error": "Note id is required"}), 400

    try:
        note_data = {
            "codeid": data["id"],
            "collection": data.get("collection", "default"),
            "text": data.get("text", ""),
            "color": data.get("color", 0),
            "position": (
                float(data.get("x", 40)),
                float(data.get("y", 40))
            ),
            "background_color": data.get("backgroundColor", "#FFFF88"),
            "border_color": data.get("borderColor", "#d8c95f")
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

        if "backgroundColor" in data:
            note_data["background_color"] = data["backgroundColor"]
        
        if "borderColor" in data:
            note_data["border_color"] = data["borderColor"]

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
    app.run(debug=True, port=5000)

    
