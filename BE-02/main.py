from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
import sqlite3

app = FastAPI()

conn = sqlite3.connect("tasks.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Endpoints
@app.get("/")
def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
def health():
    return { "status": "ok" }

# Stage 1
@app.get("/tasks")
def get_tasks():

    c.execute("SELECT * FROM tasks")
    return [dict(row) for row in c.fetchall()]

@app.get("/tasks/{id}")
def get_task(id: int):
    c.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = c.fetchone()

    if not row:
        return JSONResponse(
                status_code=404,
                content={"error": f"Task {id} not found"}
            )

    return dict(row)

# Stage 2
@app.post("/tasks")
def create_task(task: dict):

    # Validate input
    if "title" not in task:
        return JSONResponse(
            status_code=400,
            content={"error": "Task title is missing"}
        )

    # Ensure the title is a string
    if not isinstance(task["title"], str):
        return JSONResponse(
            status_code=400,
            content={"error": "Task title must be a string"}
        )

    # Validate cleaned title
    task["title"] = task["title"].strip()

    if task["title"] == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Task title is empty"}
        )

    # DEPRECATE: Assign a new ID to the task
    # new_id = max(tasks.keys())+ 1 if tasks else 1
    # ---------------------------------------------
    # SQLite INTEGER PRIMARY KEY AUTOINCREMENTS

    # Assign the new ID to the task and set done to default False
    new_task = {
        "title": task["title"],
        "done": False
    }

    # Add new task to the tasks database
    c.execute("INSERT INTO tasks (title, done) VALUES (:title, :done) RETURNING id, title, done", new_task)

    upd_row = dict(c.fetchone())
    conn.commit()

    upd_row["done"] = bool(upd_row["done"])

    return JSONResponse(
        status_code=201,
        content=upd_row
    )

# Stage 3
@app.put("/tasks/{id}")
def update_task(id: int, task: dict):

    # Validate if task is empty or invalid
    title = task.get("title")
    status = task.get("done")

    # Validate title
    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
                status_code=400,
                content={"message": "Title is empty"}
            )

    # Validate status or done
    if not isinstance(status, bool):
        return JSONResponse(
                status_code=400,
                content={"message": "Done stats must be boolean"}
            )

    title = title.strip()

    c = conn.cursor()
    
    # Update the task
    update_req = {
        "title": title,
        "done": status,
        "id": id
    }

    # Update db
    c.execute("UPDATE tasks SET title = :title, done = :done WHERE id = :id RETURNING id, title, done", update_req)

    # Store updated row
    updated = c.fetchone()

    # Check if a row got updated
    if updated is None:
        return JSONResponse(
            status_code=404,
            content={"message": "Unknown task ID"}
        )
    
    conn.commit()

    updated = dict(updated)
    updated["done"] = bool(updated["done"])

    # Return the updated task
    return updated


@app.delete("/tasks/{id}")
def delete_task(id: int):

    # Delete the task
    c.execute("DELETE FROM tasks WHERE id = ?", (id,))

    # Validate if id exists
    if c.rowcount == 0:
        return JSONResponse(
            status_code=404,
            content={"message": "Unknown task ID"}
        )
    conn.commit()
    return Response(status_code=204)
    