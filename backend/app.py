from flask import Flask, jsonify, request, send_from_directory
import os
import json

# Point Flask to the React build folder
app = Flask(
    __name__,
    static_folder="../frontend/build",
    static_url_path="/"
)

DATA_FILE = "todos.json"


# ------------------------
# Load / Save Functions
# ------------------------

def load_todos():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def save_todos(todos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)


# ------------------------
# Persistent todo storage
# ------------------------

todos = load_todos()
next_id = max([t["id"] for t in todos], default=0) + 1


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
    save_todos(todos)   # ✅ save after adding
    return jsonify(todo), 201


@app.route("/api/todos/<int:todo_id>", methods=["PATCH"])
def toggle_todo(todo_id):
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = not todo["done"]
            save_todos(todos)   # ✅ save after update
            return jsonify(todo)
    return jsonify({"error": "Not found"}), 404


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    global todos
    todos = [t for t in todos if t["id"] != todo_id]
    save_todos(todos)   # ✅ save after delete
    return jsonify({"ok": True})


# ------------------------
# REACT FRONTEND ROUTES
# ------------------------

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    build_dir = app.static_folder
    full_path = os.path.join(build_dir, path)

    if path != "" and os.path.exists(full_path):
        return send_from_directory(build_dir, path)

    return send_from_directory(build_dir, "index.html")


if __name__ == "__main__":
    app.run(debug=True)
