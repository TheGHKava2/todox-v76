from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="ToDoX Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para teste - depois restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "ToDoX Backend is running!", "status": "ok"}

@app.get("/projects")
def get_projects():
    return [
        {"id": 1, "name": "Projeto de Teste", "description": "Projeto exemplo"},
        {"id": 2, "name": "ToDoX Development", "description": "Desenvolvimento do ToDoX"}
    ]

@app.get("/projects/{project_id}/tasks")
def get_tasks(project_id: int):
    return [
        {"id": 1, "title": "Tarefa 1", "status": "TODO", "project_id": project_id},
        {"id": 2, "title": "Tarefa 2", "status": "DOING", "project_id": project_id},
        {"id": 3, "title": "Tarefa 3", "status": "DONE", "project_id": project_id}
    ]

@app.post("/seed")
def seed():
    return {"ok": True, "message": "Database seeded"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)