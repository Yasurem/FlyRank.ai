from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# Dict of tasks
tasks = {
    1: {"id": 1, 
        "title": "Create a simple CRUD app", 
        "done": False 
    },

    2: {"id": 2, 
        "title": "Finish Linear Regression Lecture", 
        "done": True 
    },

    3: {"id": 3, 
        "title": "Review basic probability concepts and Bayes' Theorem", 
        "done": True 
    }
}

# Endpoints
@app.get("/")
async def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
async def health():
    return { "status": "ok" }

# Stage 2
@app.get("/tasks")
async def get_tasks():
    return tasks

@app.get("/tasks/{id}")
async def get_task(id: int):
    if id in tasks:
        return tasks[id]
    
    return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )

# Stage 3
@app.post("/tasks")
async def create_task(task: dict):

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
        content={"message": f"Done, here's your receipt.", "task": new_task}
    )

# Stage 4
@app.put("/tasks/{id}")
async def update_task(id: int, task: dict):

    # Validate if task is empty or invalid
    if not task:
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
async def delete_task(id: int):

    # Validate ID
    if id not in tasks:
        return JSONResponse(
            status_code=404,
            content={"message": "Unknown task ID"}
        )

    # Delete the task
    del tasks[id]
    return JSONResponse(
        status_code=204,
        content={"message":"No Content"}
    )
    