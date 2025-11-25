from flask import Flask, jsonify, request, send_from_directory
import os

# Point Flask to the React build folder
app = Flask(
    __name__,
    static_folder="../frontend/build",   # path from backend/ to build/
    static_url_path="/"
)

# ------------------------
# In-memory todo storage
# ------------------------
todos = []
next_id = 1


# ------------------------
# API ROUTES (backend)
# ------------------------

@app.route("/api/todos", methods=["GET"])
def get_todos():
    return jsonify(todos)


@app.route("/api/todos", methods=["POST"])
def add_todo():
    global next_id
    data = request.get_json() or {}

    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Text is required"}), 400

    todo = {
        "id": next_id,
        "text": text,
        "done": False,
        "date": data.get("date"),
        "time": data.get("time"),
        "priority": data.get("priority", "medium"),
    }
    todos.append(todo)
    next_id += 1
    return jsonify(todo), 201


@app.route("/api/todos/<int:todo_id>", methods=["PATCH"])
def toggle_todo(todo_id):
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = not todo["done"]
            return jsonify(todo)
    return jsonify({"error": "Not found"}), 404


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    global todos
    todos = [t for t in todos if t["id"] != todo_id]
    return jsonify({"ok": True})


# ------------------------
# REACT FRONTEND ROUTES
# ------------------------

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    """
    Serve the React build files.
    Any unknown route -> index.html (so React router works).
    """
    build_dir = app.static_folder

    # If the requested file exists (e.g. /static/js/main.js), serve it
    full_path = os.path.join(build_dir, path)
    if path != "" and os.path.exists(full_path):
        return send_from_directory(build_dir, path)

    # Otherwise, serve index.html (the React SPA)
    return send_from_directory(build_dir, "index.html")


if __name__ == "__main__":
    # debug=True for development; use False for final demo if you like
    app.run(debug=True)
