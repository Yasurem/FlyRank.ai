import os, uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import repository

# Load env file
load_dotenv()

# ----------------------------------------------------------
# |            DATA TRANSFER OBJECTS (PYDANTIC)
# ----------------------------------------------------------
class TaskCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Title cannot be empty or whitespace.")
        return stripped


class TaskUpdate(BaseModel):
    title: str
    done: bool

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Title cannot be empty or whitespace.")
        return stripped

# ----------------------------------------------------------
# | LIFESPAN MANAGER
# ----------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    repository.setup_database()
    yield


# ----------------------------------------------------------
# | INIT APP AND AI ENDPOINTS
# ----------------------------------------------------------
app = FastAPI(lifespan=lifespan)

# Endpoints
@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "ok"}

# Stage 1
@app.get("/tasks")
def get_tasks():
    return repository.get_all_tasks()

@app.get("/tasks/{id}")
def get_task(id: int):
    row = repository.get_task(id)

    if not row or row is None:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found."})

    return row

# Stage 2
@app.post("/tasks")
def create_task(task: TaskCreate):
    # Assign the new ID to the task and set done to default False
    new_task = repository.create_task(title=task.title, done=False)

    return JSONResponse(
        status_code=201,
        content=new_task
    )

# Stage 3
@app.put("/tasks/{id}")
def update_task(id: int, task: TaskUpdate):
    # Update the task
    updated = repository.update_task(task_id=id, title=task.title, done=task.done)

    # Check if a row got updated
    if updated is None:
        return JSONResponse(
            status_code=404,
            content={"message": "Unknown task ID"}
        )

    # Return the updated task
    return updated

@app.delete("/tasks/{id}")
def delete_task(id: int):
    success = repository.delete_task(task_id=id)

    if not success:
        return JSONResponse(
            status_code=404,
            content={"message": "Unknown task ID"}
        )

    return Response(status_code=204)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)