from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import datetime
from typing import List, Optional, Dict, Any
import io, zipfile, os, json, threading, time
from pathlib import Path

# In-memory storage (substituto do SQLite para o Render)
PROJECTS = {}  # id -> {id, name, created_at}
TASKS = {}     # id -> {id, project_id, title, description_md, status, priority, order_index, created_at}
AGENTS = {}    # id -> {id, name, capabilities, max_concurrency}
TASK_RUNS = {} # id -> {id, task_id, agent_id, status, summary_md, started_at, ended_at}
PULL_REQUESTS = {} # id -> {id, task_run_id, title, description}

# Counters para IDs
PROJECT_COUNTER = 1
TASK_COUNTER = 1
AGENT_COUNTER = 1
RUN_COUNTER = 1
PR_COUNTER = 1

# Status enums simulados
class TaskStatus:
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"

app = FastAPI(title="ToDoX Backend - Render Compatible", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "ToDoX Backend is running!", "status": "ok", "storage": "memory"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ToDoX Backend", "projects": len(PROJECTS), "tasks": len(TASKS)}

# -------- Projects --------
@app.post("/projects")
def create_project(payload: dict):
    global PROJECT_COUNTER
    if not payload.get("name"):
        raise HTTPException(400, "Name is required")
    
    # Verificar se já existe
    for p in PROJECTS.values():
        if p["name"] == payload["name"]:
            raise HTTPException(400, "Project with this name already exists")
    
    project = {
        "id": PROJECT_COUNTER,
        "name": payload["name"],
        "created_at": datetime.utcnow().isoformat()
    }
    PROJECTS[PROJECT_COUNTER] = project
    PROJECT_COUNTER += 1
    
    return project

@app.get("/projects")
def list_projects():
    return list(PROJECTS.values())

# -------- Agents --------
@app.post("/agents")
def create_agent(payload: dict):
    global AGENT_COUNTER
    agent = {
        "id": AGENT_COUNTER,
        "name": payload.get("name", f"Agent {AGENT_COUNTER}"),
        "capabilities": payload.get("capabilities", []),
        "max_concurrency": payload.get("max_concurrency", 1)
    }
    AGENTS[AGENT_COUNTER] = agent
    AGENT_COUNTER += 1
    return agent

@app.get("/agents")
def list_agents():
    return list(AGENTS.values())

# -------- Tasks --------
@app.post("/projects/{project_id}/tasks")
def create_task(project_id: int, payload: dict):
    global TASK_COUNTER
    
    if project_id not in PROJECTS:
        raise HTTPException(404, "Project not found")
    
    # Calcular próxima order_index
    max_order = 0
    for task in TASKS.values():
        if task["project_id"] == project_id and task.get("order_index", 0) > max_order:
            max_order = task["order_index"]
    
    task = {
        "id": TASK_COUNTER,
        "project_id": project_id,
        "title": payload.get("title", "Untitled Task"),
        "description_md": payload.get("description_md", ""),
        "status": TaskStatus.TODO,
        "priority": payload.get("priority", 3),
        "order_index": max_order + 10,
        "assignee": None,
        "created_at": datetime.utcnow().isoformat()
    }
    TASKS[TASK_COUNTER] = task
    TASK_COUNTER += 1
    
    return task

@app.get("/projects/{project_id}/tasks")
def list_tasks(project_id: int):
    if project_id not in PROJECTS:
        raise HTTPException(404, "Project not found")
    
    project_tasks = [t for t in TASKS.values() if t["project_id"] == project_id]
    # Ordenar por order_index, priority, created_at
    project_tasks.sort(key=lambda x: (x.get("order_index", 999999), -x.get("priority", 3), x.get("created_at", "")))
    
    return project_tasks

@app.patch("/tasks/{task_id}/reorder")
def reorder_task(task_id: int, payload: dict):
    if task_id not in TASKS:
        raise HTTPException(404, "Task not found")
    
    new_order = payload.get("new_order_index", payload.get("order_index"))
    if new_order is not None:
        TASKS[task_id]["order_index"] = new_order
    
    return {"ok": True}

# -------- Claim Next --------
@app.post("/projects/{project_id}/claim-next")
def claim_next(project_id: int, payload: dict):
    global RUN_COUNTER
    
    if project_id not in PROJECTS:
        raise HTTPException(404, "Project not found")
    
    agent_id = payload.get("agent_id")
    if not agent_id:
        raise HTTPException(400, "agent_id is required")
    
    # Buscar próxima tarefa TODO
    eligible_tasks = [
        t for t in TASKS.values() 
        if t["project_id"] == project_id and t["status"] == TaskStatus.TODO
    ]
    
    if not eligible_tasks:
        return {"task": None, "run_id": None}
    
    # Ordenar e pegar primeira
    eligible_tasks.sort(key=lambda x: (x.get("order_index", 999999), -x.get("priority", 3), x.get("created_at", "")))
    task = eligible_tasks[0]
    
    # Marcar como IN_PROGRESS
    task["status"] = TaskStatus.IN_PROGRESS
    task["assignee"] = f"agent:{agent_id}"
    
    # Criar run
    run = {
        "id": RUN_COUNTER,
        "task_id": task["id"],
        "agent_id": agent_id,
        "status": "RUNNING",
        "started_at": datetime.utcnow().isoformat(),
        "ended_at": None,
        "summary_md": None
    }
    TASK_RUNS[RUN_COUNTER] = run
    RUN_COUNTER += 1
    
    return {"task": task, "run_id": run["id"]}

# -------- Finish --------
@app.post("/tasks/{task_id}/finish")
def finish_task(task_id: int, payload: dict):
    global PR_COUNTER
    
    if task_id not in TASKS:
        raise HTTPException(404, "Task not found")
    
    run_id = payload.get("run_id")
    if not run_id or run_id not in TASK_RUNS:
        raise HTTPException(404, "Run not found")
    
    task = TASKS[task_id]
    run = TASK_RUNS[run_id]
    
    # Atualizar run
    run["summary_md"] = payload.get("summary_md", "")
    run["ended_at"] = datetime.utcnow().isoformat()
    run["status"] = payload.get("status", "SUCCESS")
    
    # Atualizar task status
    status = payload.get("status", "SUCCESS")
    if status == "SUCCESS":
        task["status"] = TaskStatus.DONE
    elif status == "BLOCKED":
        task["status"] = TaskStatus.BLOCKED
    elif status == "FAILED":
        task["status"] = TaskStatus.FAILED
    
    # Criar PR se solicitado
    pr_id = None
    if payload.get("create_pr") and status == "SUCCESS":
        pr = {
            "id": PR_COUNTER,
            "task_run_id": run_id,
            "title": payload.get("pr_title", f"Task #{task_id} - Auto PR"),
            "description": payload.get("pr_description", ""),
            "diff_summary": payload.get("pr_diff_summary", ""),
            "created_at": datetime.utcnow().isoformat()
        }
        PULL_REQUESTS[PR_COUNTER] = pr
        pr_id = PR_COUNTER
        PR_COUNTER += 1
    
    return {"ok": True, "task_status": task["status"], "pr_id": pr_id}

# -------- PRs --------
@app.get("/pull-requests")
def list_prs():
    return list(PULL_REQUESTS.values())

# -------- Scaffold --------
@app.get("/projects/{project_id}/scaffold")
def scaffold_project(project_id: int):
    if project_id not in PROJECTS:
        raise HTTPException(404, "Project not found")
    
    project = PROJECTS[project_id]
    project_tasks = [t for t in TASKS.values() if t["project_id"] == project_id]
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # Basic structure
        z.writestr(".gitignore", ".venv/\n__pycache__/\nnode_modules/\n.env\n")
        z.writestr("README.md", f"# {project['name']}\n\nGerado pelo ToDoX\n")
        
        # Tasks YAML
        tasks_yaml = f"""version: 1
project: {project['name']}
policy:
  pick_rule: first_by_order
  edit_guard: touch_only_related
tasks:
"""
        for task in sorted(project_tasks, key=lambda x: x.get("order_index", 999999)):
            tasks_yaml += f"""  - id: T-{task['id']:03d}
    order: {task.get('order_index', 1000000)}
    title: {task['title']}
    description: "{task.get('description_md', '').replace('"', '\\"')}"
    status: {task['status']}
    priority: P{task.get('priority', 3)}
    assignees: [agent:*]
    depends_on: []
    dod: []
    outputs: []
    notes: ""
"""
        
        z.writestr("todox/TASKS.yaml", tasks_yaml)
        z.writestr("todox/DOD.md", "# Definition of Done\n- lint_ok\n- tests_pass\n")
        z.writestr("todox/RUNS/.keep", "")
        
    buf.seek(0)
    headers = {"Content-Disposition": f"attachment; filename=project_{project_id}_scaffold.zip"}
    return StreamingResponse(buf, media_type="application/zip", headers=headers)

# -------- Seed (dados de exemplo) --------
@app.post("/seed")
def seed():
    global PROJECT_COUNTER, TASK_COUNTER, AGENT_COUNTER
    
    # Projeto demo
    if not any(p["name"] == "Projeto Demo" for p in PROJECTS.values()):
        project = {
            "id": PROJECT_COUNTER,
            "name": "Projeto Demo", 
            "created_at": datetime.utcnow().isoformat()
        }
        PROJECTS[PROJECT_COUNTER] = project
        project_id = PROJECT_COUNTER
        PROJECT_COUNTER += 1
        
        # Agentes
        if not AGENTS:
            for i in range(1, 3):
                agent = {
                    "id": AGENT_COUNTER,
                    "name": f"Agente {i}",
                    "capabilities": ["coding", "testing"],
                    "max_concurrency": 1
                }
                AGENTS[AGENT_COUNTER] = agent
                AGENT_COUNTER += 1
        
        # Tarefas
        task_titles = [
            "Configurar repositório e CI",
            "Criar endpoint GET /status", 
            "Implementar claim-next",
            "UI: listar tarefas e criar nova",
            "Worker: executar tarefa e gerar PR simulado"
        ]
        
        for i, title in enumerate(task_titles):
            task = {
                "id": TASK_COUNTER,
                "project_id": project_id,
                "title": title,
                "description_md": f"Descrição da tarefa: {title}",
                "status": TaskStatus.TODO,
                "priority": 3,
                "order_index": (i + 1) * 10,
                "assignee": None,
                "created_at": datetime.utcnow().isoformat()
            }
            TASKS[TASK_COUNTER] = task
            TASK_COUNTER += 1
        
        return {"ok": True, "project_id": project_id, "tasks": len(task_titles)}
    
    return {"ok": True, "message": "Demo data already exists"}

# -------- Info endpoint --------
@app.get("/info")
def get_info():
    return {
        "projects": len(PROJECTS),
        "tasks": len(TASKS),
        "agents": len(AGENTS),
        "runs": len(TASK_RUNS),
        "prs": len(PULL_REQUESTS),
        "storage": "in-memory",
        "platform": "render"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)