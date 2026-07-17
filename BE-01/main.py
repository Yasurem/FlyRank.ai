from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# Dict of tasks
tasks = {
    1: {"id": 1, "title": "Create a simple CRUD app", "completed": False },
    2: {"id": 2, "title": "Finish Linear Regression Lecture", "completed": True },
    3: {"id": 3, "title": "Review basic probability concepts and Bayes' Theorem", "completed": True }
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