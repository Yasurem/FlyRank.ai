# Task API: A Basic To-Do List Manager CRUD API

---

## Overview

---

This project was created by **Joemarc Jr. D. Castillo** for compliance with the **FlyRank Internship** Requirement ***Build you first CRUD API*** also known as _Assignment A1_ or _BE-01_ under the Backend AI Engineering Track. This README markdown file, specifically, is a requirement to accomplish __Stage 6__ _(Publish to Github)_ of this assignment. In summary, **all six required stages were successfully implemented for this project.**

## Dependencies, Installation, and Execution
*Note: Running these commands in a virtual environment(.venv) would be useful, especially if you don't plan to use the dependencies in this project elsewhere.*

##### Project Dependencies:
Python 3.12+
FastAPI Library

##### Installation
In your terminal, install the FastAPI library using the Python Package Installer (pip) 
`pip install "fastapi[standard]"`

##### Execution
`fastapi dev`

---

## Endpoints
| HTTP Method | Route | Description | Success Status | Client Error Status |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Returns base routing metadata. | `200 OK` | None |
| `GET` | `/health` | Returns server health status. | `200 OK` | None |
| `GET` | `/tasks` | Retrieves the complete collection of task objects. | `200 OK` | None |
| `GET` | `/tasks/{id}` | Retrieves a single task object mapped to the integer ID. | `200 OK` | `404 Not Found` |
| `POST` | `/tasks` | Instantiates a new task. Requires a JSON payload containing a valid `"title"` string. | `201 Created` | `400 Bad Request` |
| `PUT` | `/tasks/{id}` | Mutates an existing task state. Replaces existing keys with the provided JSON payload. | `200 OK` | `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/tasks/{id}` | Destroys the task record mapped to the integer ID. Returns an empty envelope. | `204 No Content` | `404 Not Found` |

---

## Example Execution
The following demonstrates a standard HTTP `POST` request to create a new task, executed via `curl`, alongside the strict response headers and serialized JSON payload returned by the server.

**Command:**
```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title": "Finish CS50x Final Project"}'
```

**Output:**
```text
HTTP/1.1 201 Created
date: Sat, 18 Jul 2026 11:29:10 GMT
server: uvicorn
content-length: 58
content-type: application/json

{"id":4,"title":"Finish CS50x Final Project","done":false}
```