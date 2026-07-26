from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
import sqlite3

app = FastAPI()

conn = sqlite3.connect("tasks.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Endpoints
# Stage 1
@app.get("/")
def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
def health():
    return { "status": "ok" }

# Stage 2
@app.get("/tasks")
def get_tasks():
    c.execute("SELECT * FROM tasks")
    rows = []
    for row in c.fetchall():
        rows = dict(row)

    return rows

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

# Stage 3
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

    # Assign a new ID to the task
    new_id = max(tasks.keys())+ 1 if tasks else 1

    # Assign the new ID to the task and set done to default False
    new_task = {
        "id": new_id,
        "title": task["title"],
        "done": False
    }

    # Add it to the tasks dictionary
    tasks[new_id] = new_task

    return JSONResponse(
        status_code=201,
        content=new_task
    )

# Stage 4
@app.put("/tasks/{id}")
def update_task(id: int, task: dict):

    # Validate if task is empty or invalid
    if not task or task.get("title").strip()=="":
        return JSONResponse(
            status_code=400,
            content={"error": "Empty or invalid body"}
        )
    
    # Check if task exists in db
    if id not in tasks:
        return JSONResponse(
            status_code=404,
            content={"message": "Unknown task ID"}
        )
    
    # Update the task
    tasks[id].update(task)

    # Return the updated task
    return tasks[id]


@app.delete("/tasks/{id}")
def delete_task(id: int):

    # Validate ID
    if id not in tasks:
        return JSONResponse(
            status_code=404,
            content={"message": "Unknown task ID"}
        )

    # Delete the task
    del tasks[id]
    return Response(status_code=204)
    