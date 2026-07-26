from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sqlite3, os, sys, uvicorn

conn = None

# ----------------------------------------------------------
# |                     SEED DATABASE                      
# ----------------------------------------------------------
def execute_seed(db_path: str, sql_file_path: str) -> None:
    if not os.path.exists(sql_file_path):
        print(f"Error: Seed file '{sql_file_path}' missing.", file=sys.stderr)
        sys.exit(1)
        
    with open(sql_file_path, "r", encoding="utf-8") as file:
        sql_script = file.read()
        
    with sqlite3.connect(db_path, timeout=5.0) as conn:
        conn.executescript(sql_script)
        print(f"Successfully seeded {db_path} using {sql_file_path}")


# ----------------------------------------------------------
# |                  LIFESPAN MANAGER                      
# ----------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global conn
    
    # 1. Guarantee directory exists before establishing the persistent connection
    os.makedirs("database", exist_ok=True)
    
    # 2. Execute the seed script
    execute_seed("database/tasks.db", "database/seed.sql")
    
    # 3. Initialize the global database connection
    conn = sqlite3.connect("database/tasks.db", check_same_thread=False, timeout=5.0)
    conn.row_factory = sqlite3.Row
    
    yield  # Server handles requests here
    
    # 4. Teardown: Safely close the global connection on server shutdown
    if conn:
        conn.close()


# ----------------------------------------------------------
# |                  CONNECT TO DATABASE                      
# ----------------------------------------------------------
conn = sqlite3.connect("database/tasks.db", check_same_thread=False)
conn.row_factory = sqlite3.Row


# ----------------------------------------------------------
# |               INIT APP AND AI ENDPOINTS                      
# ----------------------------------------------------------
app = FastAPI(lifespan=lifespan)


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
    c = conn.cursor()
    c.execute("SELECT * FROM tasks")

    return [dict(row) for row in c.fetchall()]


@app.get("/tasks/{id}")
def get_task(id: int):
    c = conn.cursor()
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
    c = conn.cursor()

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

    c = conn.cursor()

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


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)