import os

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

from models import db, Task

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "task-api"
    })


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()

    return jsonify([
        task.to_dict()
        for task in tasks
    ])


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({
            "error": "Task title is required"
        }), 400

    task = Task(
        title=data["title"],
        description=data.get("description")
    )

    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({
            "error": "Task not found"
        }), 404

    data = request.get_json()

    if "title" in data:
        task.title = data["title"]

    if "description" in data:
        task.description = data["description"]

    if "completed" in data:
        task.completed = data["completed"]

    db.session.commit()

    return jsonify(task.to_dict())


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({
            "error": "Task not found"
        }), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "message": "Task deleted successfully"
    })


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000)
