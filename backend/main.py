
import os
import platform
from pathlib import Path

ID_PAD_DEFAULT = int(os.environ.get("TODOX_ID_PAD", "7"))
MAX_PATH_TARGET = int(os.environ.get("TODOX_MAX_PATH", "200"))  # alvo seguro p/ Windows clássico

def _sanitize_fs_segment(name: str, is_windows: bool = False, maxlen: int = 200) -> str:
    """Sanitize a string to be safe for filesystem use"""
    # Remove or replace unsafe characters
    import re
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    # Truncate if too long
    if len(sanitized) > maxlen:
        sanitized = sanitized[:maxlen].rstrip('. ')
    return sanitized or "untitled"

def _format_project_dirname(project_id: int, name: str, pad: int = ID_PAD_DEFAULT) -> str:
    pid = str(project_id).zfill(pad)
    clean = _sanitize_fs_segment(name, platform.system().lower().startswith("win"), maxlen=200)
    return f"{pid} - {clean}"

def _truncate_dirname_for_path(base: Path, dirname: str, extra_len: int = 0) -> str:
    # Garante que base/dirname (mais alguns arquivos) não ultrapasse MAX_PATH_TARGET
    total = len(str(base / dirname))
    if total + extra_len <= MAX_PATH_TARGET:
        return dirname
    # reduzir o nome após ' - '
    if " - " in dirname:
        prefix, sep, rest = dirname.partition(" - ")
        budget = max(10, MAX_PATH_TARGET - len(str(base / (prefix + sep))) - extra_len)
        truncated = rest[:budget]
        # evitar cortar em espaço/UTF-8 estranho
        truncated = truncated.rstrip(" .")
        return prefix + sep + truncated
    return dirname[:MAX_PATH_TARGET - len(str(base)) - 1]

def _ensure_unique_path(p: Path) -> Path:
    if not p.exists():
        return p
    n = 2
    while True:
        candidate = p.parent / f"{p.name} - ({n})"
        if not candidate.exists():
            return candidate
        n += 1

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from datetime import datetime
from typing import List, Optional
import io, zipfile, os, json, subprocess, sys, yaml, re, threading, time
from pathlib import Path

from database import SessionLocal, init_db
import models
from schemas import *

SAFE_SCAFFOLD_ROOT = os.getenv("SAFE_SCAFFOLD_ROOT", "")  # opcional: restringe destino
WATCHERS = {}  # project_id -> {"thread":Thread, "path":Path, "yaml_rel":"todox/TASKS.yaml", "stop":Event}

app = FastAPI(title="ToDoX MVP API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "ToDoX Backend"}

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "ToDoX MVP API", "version": "0.3.0", "docs": "/docs"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    init_db()

# --- SSE & Sync globals ---
from fastapi import Request
from fastapi.responses import StreamingResponse
import asyncio, hashlib

EVENT_SUBSCRIBERS: dict[int, list[asyncio.Queue]] = {}
def _get_subscribers(project_id: int):
    if project_id not in EVENT_SUBSCRIBERS:
        EVENT_SUBSCRIBERS[project_id] = []
    return EVENT_SUBSCRIBERS[project_id]

def _json_dumps(obj):
    try:
        import json
        return json.dumps(obj, default=str, ensure_ascii=False)
    except Exception:
        return "{}"

async def _emit(project_id: int, event_type: str, payload: dict):
    queues = _get_subscribers(project_id)
    msg = {"type": event_type, "payload": payload}
    data = _json_dumps(msg)
    for q in list(queues):
        # SSE queue
        try:
            await q.put(data)
        except Exception:
            pass

def _hash_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def _write_yaml_to_repo_if_watched(project_id: int):
    # escreve DB -> arquivo quando há watcher ativo (bidirecional)
    w = WATCHERS.get(project_id)
    if not w: return
    repo = Path(w["path"]); rel = w["yaml_rel"]
    target = (repo / rel)
    target.parent.mkdir(parents=True, exist_ok=True)
    # gerar YAML atual
    yaml_text = _build_tasks_yaml(SessionLocal(), project_id) if callable(_build_tasks_yaml) else None  # fallback seguro
    if yaml_text is None:
        # no contexto, usamos a função existente com DB externo
        db = SessionLocal()
        try:
            yaml_text = _build_tasks_yaml(db, project_id)
        finally:
            db.close()
    content = yaml_text.encode("utf-8")
    h = _hash_bytes(content)
    # se alteração veio do arquivo (hash visto), evite loop
    last_file_hash = w.get("last_file_hash")
    if last_file_hash and last_file_hash == h:
        return
    # se for igual ao último export, evite reescrever
    if w.get("last_export_hash") == h:
        return
    target.write_bytes(content)
    w["last_export_hash"] = h

@app.get("/events/stream")
async def events_stream(project_id: int, request: Request):
    q: asyncio.Queue = asyncio.Queue()
    subs = _get_subscribers(project_id)
    subs.append(q)
    async def gen():
        # keepalive inicial
        yield "event: ping\ndata: {}\n\n"
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(q.get(), timeout=25)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    # keepalive para evitar timeouts em proxies
                    yield "event: ping\ndata: {}\n\n"
        finally:
            if q in subs:
                subs.remove(q)
    return StreamingResponse(gen(), media_type="text/event-stream", headers={"Cache-Control":"no-cache", "X-Accel-Buffering":"no"})

# --- WebSocket support (além de SSE) ---
WS_SUBSCRIBERS: dict[int, list[WebSocket]] = {}

def _get_ws_subs(project_id: int):
    if project_id not in WS_SUBSCRIBERS:
        WS_SUBSCRIBERS[project_id] = []
    return WS_SUBSCRIBERS[project_id]

@app.websocket("/ws/events")
async def ws_events(websocket: WebSocket, project_id: int):
    await websocket.accept()
    subs = _get_ws_subs(project_id)
    subs.append(websocket)
    try:
        while True:
            # mantemos a conexão viva; não esperamos mensagens do cliente
            msg = await websocket.receive_text()
            # ignore input; protocolo unidirecional (server push)
            # opcional: 'ping' do cliente
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in subs:
            subs.remove(websocket)

# -------- Projects --------
@app.post("/projects", response_model=ProjectOut)
async def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    if db.scalar(select(models.Project).where(models.Project.name==payload.name)):
        raise HTTPException(400, "Project with this name already exists")
    p = models.Project(name=payload.name)
    db.add(p); db.commit(); db.refresh(p)
    await _emit(p.id, "project.created", {"id": p.id, "name": p.name})
    return p

@app.get("/projects", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    try:
        projects = db.scalars(select(models.Project).order_by(models.Project.id)).all()
        return projects
    except Exception as e:
        # Se erro, provavelmente tabelas não existem - criar
        try:
            from database import init_db
            init_db()
            projects = db.scalars(select(models.Project).order_by(models.Project.id)).all()
            return projects
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e2)}")

# -------- Agents --------
@app.post("/agents", response_model=AgentOut)
def create_agent(payload: AgentCreate, db: Session = Depends(get_db)):
    ag = models.Agent(name=payload.name, capabilities=payload.capabilities, max_concurrency=payload.max_concurrency)
    db.add(ag); db.commit(); db.refresh(ag)
    return ag

@app.get("/agents", response_model=List[AgentOut])
def list_agents(db: Session = Depends(get_db)):
    return db.scalars(select(models.Agent).order_by(models.Agent.id)).all()

# -------- Tasks --------
@app.post("/projects/{project_id}/tasks", response_model=TaskOut)
async def create_task(project_id: int, payload: TaskCreate, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    max_order = db.scalar(select(func.max(models.Task.order_index)).where(models.Task.project_id==project_id)) or 0
    t = models.Task(project_id=project_id, title=payload.title, description_md=payload.description_md, priority=payload.priority, order_index=max_order+10)
    db.add(t); db.commit(); db.refresh(t)
    _write_yaml_to_repo_if_watched(project_id)
    await _emit(project_id, "task.created", {"id": t.id, "title": t.title})
    return t

@app.get("/projects/{project_id}/tasks", response_model=List[TaskOut])
def list_tasks(project_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(models.Task).where(models.Task.project_id==project_id).order_by(models.Task.order_index.asc(), models.Task.priority.desc(), models.Task.created_at.asc())).all()

@app.post("/tasks/{task_id}/dependency/{depends_on_id}")
def add_dependency(task_id: int, depends_on_id: int, db: Session = Depends(get_db)):
    t = db.get(models.Task, task_id); d = db.get(models.Task, depends_on_id)
    if not t or not d:
        raise HTTPException(404, "Task(s) not found")
    dep = models.TaskDependency(task_id=task_id, depends_on_task_id=depends_on_id)
    db.add(dep); db.commit()
    return {"ok": True}

@app.patch("/tasks/{task_id}/reorder")
async def reorder_task(task_id: int, new_order_index: int, db: Session = Depends(get_db)):
    t = db.get(models.Task, task_id)
    if not t: raise HTTPException(404, "Task not found")
    t.order_index = new_order_index
    db.commit()
    _write_yaml_to_repo_if_watched(t.project_id)
    await _emit(t.project_id, "task.reordered", {"id": t.id, "order": t.order_index})
    return {"ok": True}

# -------- Claim Next --------
def has_open_dependencies(db: Session, task_id: int) -> bool:
    deps = db.scalars(select(models.TaskDependency).where(models.TaskDependency.task_id==task_id)).all()
    for dep in deps:
        st = db.get(models.Task, dep.depends_on_task_id).status
        if st != models.TaskStatus.DONE:
            return True
    return False

@app.post("/projects/{project_id}/claim-next", response_model=ClaimResponse)
def claim_next(project_id: int, payload: ClaimRequest, db: Session = Depends(get_db)):
    db.begin()
    try:
        q = select(models.Task).where(
            and_(
                models.Task.project_id==project_id,
                models.Task.status==models.TaskStatus.TODO
            )
        ).order_by(models.Task.order_index.asc(), models.Task.priority.desc(), models.Task.created_at.asc())
        for task in db.scalars(q):
            if not has_open_dependencies(db, task.id):
                task.status = models.TaskStatus.IN_PROGRESS
                task.assignee = f"agent:{payload.agent_id}"
                run = models.TaskRun(task_id=task.id, agent_id=payload.agent_id, status="RUNNING")
                db.add(run)
                db.commit()
                db.refresh(run); db.refresh(task)
                return ClaimResponse(task=task, run_id=run.id)
        db.commit()
        return ClaimResponse(task=None, run_id=None)
    except Exception:
        db.rollback()
        raise

# -------- Finish --------
@app.post("/tasks/{task_id}/finish")
async def finish_task(task_id: int, payload: FinishRequest, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task: raise HTTPException(404, "Task not found")
    run = db.get(models.TaskRun, payload.run_id)
    if not run: raise HTTPException(404, "Run not found")
    import models as m
    for a in payload.artifacts:
        art = m.Artifact(task_run_id=run.id, type=a.type, uri=a.uri, hash=a.hash, metadata_json=a.metadata_json)
        db.add(art)
    run.summary_md = payload.summary_md
    run.ended_at = datetime.utcnow()
    run.status = payload.status
    if payload.status == "SUCCESS":
        task.status = models.TaskStatus.DONE
    elif payload.status == "BLOCKED":
        task.status = models.TaskStatus.BLOCKED
    elif payload.status == "FAILED":
        task.status = models.TaskStatus.FAILED
    db.commit()
    pr_id = None
    if payload.create_pr and payload.status == "SUCCESS":
        pr = models.PullRequest(task_run_id=run.id, title=payload.pr_title or f"Tarefa #{task.id} - PR automático", description=payload.pr_description or "", diff_summary=payload.pr_diff_summary or "")
        db.add(pr); db.commit(); db.refresh(pr)
        pr_id = pr.id
    _write_yaml_to_repo_if_watched(task.project_id)
    await _emit(task.project_id, "task.finished", {"id": task.id, "status": task.status.value, "pr_id": pr_id})
    return {"ok": True, "task_status": task.status.value, "pr_id": pr_id}

# -------- PRs --------
@app.get("/pull-requests", response_model=List[PullRequestOut])
def list_prs(db: Session = Depends(get_db)):
    return db.scalars(select(models.PullRequest).order_by(models.PullRequest.id.desc())).all()

# ------------- Scaffold helpers ---------------
def _priority_label(n: int) -> str:
    try:
        n = int(n or 3)
    except Exception:
        n = 3
    return {1:"P1", 2:"P2", 3:"P3", 4:"P4"}.get(n, "P3")

def _build_tasks_yaml(db: Session, project_id: int) -> str:
    tasks = db.scalars(select(models.Task).where(models.Task.project_id==project_id).order_by(models.Task.order_index.asc(), models.Task.priority.desc(), models.Task.created_at.asc())).all()
    lines = []
    project = db.get(models.Project, project_id)
    pname = project.name if project else f"Projeto {project_id}"
    lines += ["version: 1", f"project: {pname}", "policy:", "  pick_rule: first_by_order", "  edit_guard: touch_only_related", "tasks:"]
    for t in tasks:
        dep_rels = db.scalars(select(models.TaskDependency).where(models.TaskDependency.task_id==t.id)).all()
        dep_ids = [f"T-{rel.depends_on_task_id:03d}" for rel in dep_rels]
        tid = f"T-{t.id:03d}"
        prio = _priority_label(t.priority)
        desc = (t.description_md or "").replace("\n"," ").replace('"','\\"')
        lines += [
            f"  - id: {tid}",
            f"    order: {t.order_index if t.order_index is not None else 1000000}",
            f"    title: {t.title.replace(':',' -')}",
            f"    description: \"{desc}\"",
            f"    status: TODO",
            f"    priority: {prio}",
            f"    assignees: [agent:*]",
            f"    depends_on: [{', '.join(dep_ids)}]" if dep_ids else f"    depends_on: []",
            f"    dod: []",
            f"    outputs: []",
            f"    notes: \"\"",
        ]
    return "\n".join(lines)

def _write_common(dest: Path, tasks_yaml: str):
    (dest/".gitignore").write_text(".venv/\n__pycache__/\nnode_modules/\n.env\n", encoding="utf-8")
    (dest/".editorconfig").write_text("root = true\n[*]\ncharset = utf-8\nend_of_line = lf\ninsert_final_newline = true\nindent_style = space\nindent_size = 2\n", encoding="utf-8")
    os.makedirs(dest/".vscode", exist_ok=True)
    vscode_json = {
        "version":"2.0.0",
        "tasks":[
            {"label":"ToDox: listar","type":"shell","command":"python todox/todoctl.py list"},
            {"label":"ToDox: próxima elegível","type":"shell","command":"python todox/todoctl.py next"},
            {"label":"ToDox: iniciar (IN_PROGRESS)","type":"shell","command":"python todox/todoctl.py start ${input:taskId}"},
            {"label":"ToDox: finalizar (DONE)","type":"shell","command":"python todox/todoctl.py finish ${input:taskId}"},
            {"label":"ToDox: reordenar","type":"shell","command":"python todox/todoctl.py reorder ${input:taskId} ${input:newOrder}"}
        ],
        "inputs":[
            {"id":"taskId","type":"promptString","description":"ID da tarefa (ex.: T-001)"},
            {"id":"newOrder","type":"promptString","description":"Nova ordem (ex.: 15)"}
        ]
    }
    (dest/".vscode/tasks.json").write_text(json.dumps(vscode_json, ensure_ascii=False, indent=2), encoding="utf-8")
    os.makedirs(dest/"todox/SESSIONS", exist_ok=True)
    os.makedirs(dest/"todox/RUNS", exist_ok=True)
    (dest/"todox"/"TASKS.yaml").write_text(tasks_yaml, encoding="utf-8")
    (dest/"todox"/"DOD.md").write_text("# Definition of Done (DoD)\n- lint_ok\n- tests_pass\n- unit_coverage>=80\n- contract_test_ok\n- readme_badge\n", encoding="utf-8")
    (dest/"todox"/"PROMPT_CARD.md").write_text("# SOP — Operação de Agente ToDox\n(consulte o painel ToDoX para instruções)\n", encoding="utf-8")
    (dest/"README_TODOX.md").write_text("Estrutura gerada automaticamente pelo ToDoX.\n", encoding="utf-8")
    (dest/"todox"/"todoctl.py").write_text('#!/usr/bin/env python3\nprint("todoctl minimal — instale a versão completa do ToDoX CLI")\n', encoding="utf-8")
    return dest

def _write_code_quality(dest: Path, req: ScaffoldApplyRequest):
    # pre-commit (hook configs para ruff/black e eslint/prettier se presentes)
    (dest/".pre-commit-config.yaml").write_text("""repos:
- repo: https://github.com/psf/black
  rev: 24.8.0
  hooks:
    - id: black
      language_version: python3
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.6.9
  hooks:
    - id: ruff
      args: [--fix]
""", encoding="utf-8")
    (dest/".ruff.toml").write_text("""line-length = 100
target-version = "py311"
lint.select = ["E","F","I","UP","B","SIM"]
lint.ignore = []
""", encoding="utf-8")
    (dest/".flake8").write_text("""[flake8]
max-line-length = 100
extend-ignore = E203,W503
""", encoding="utf-8")
    (dest/".eslintrc.cjs").write_text("""module.exports = {
  env: { browser: true, es2021: true, node: true },
  extends: ['eslint:recommended', 'plugin:react/recommended'],
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  settings: { react: { version: 'detect' } },
  rules: {},
};
""", encoding="utf-8")
    (dest/".prettierrc").write_text("""{
  "semi": true,
  "singleQuote": false,
  "printWidth": 100,
  "tabWidth": 2
}
""", encoding="utf-8")
    if req.license.upper() == "MIT":
        (dest/"LICENSE").write_text(f"MIT License\n\nCopyright (c) {datetime.utcnow().year} ToDoX User\n\nPermission is hereby granted...\n", encoding="utf-8")

def _write_ci_python(dest: Path, threshold: int):
    wf = dest/".github/workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf/"ci.yml").write_text(f"""name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {{ python-version: '3.11' }}
      - run: python -m pip install --upgrade pip
      - run: pip install -r requirements.txt || true
      - run: pip install pytest pytest-cov
      - run: pytest -q --cov=. --cov-report=term-missing --cov-fail-under={threshold}
""", encoding="utf-8")

def _write_ci_node(dest: Path, threshold: int):
    wf = dest/".github/workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf/"node.yml").write_text(f"""name: Node CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {{ node-version: '20' }}
      - run: npm ci
      - run: npm test --silent
""", encoding="utf-8")
    # coverage gate will be in vitest config within the template

def _write_ci_pnpm_monorepo(dest: Path):
    wf = dest/".github/workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf/"monorepo.yml").write_text("""name: Monorepo CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm -r test
""", encoding="utf-8")

def _write_python_fastapi(dest: Path, req: ScaffoldApplyRequest):
    (dest/"requirements.txt").write_text("fastapi\nuvicorn\npytest\npytest-cov\n", encoding="utf-8")
    (dest/"app").mkdir(exist_ok=True)
    (dest/"app"/"main.py").write_text("from fastapi import FastAPI\napp=FastAPI()\n@app.get('/')\ndef hi(): return {'ok':True}\n", encoding="utf-8")
    (dest/"tests").mkdir(exist_ok=True)
    (dest/"tests"/"test_status.py").write_text("def test_truth():\n    assert True\n", encoding="utf-8")
    if req.ci: _write_ci_python(dest, req.coverage_py)

def _write_python_fastapi_sqlmodel_jwt(dest: Path, req: ScaffoldApplyRequest):
    (dest/"requirements.txt").write_text("fastapi\nuvicorn\nsqlmodel\nsqlalchemy\npython-jose[cryptography]\npasslib[bcrypt]\npytest\npytest-cov\n", encoding="utf-8")
    (dest/"app").mkdir(exist_ok=True)
    (dest/"app"/"main.py").write_text("""from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from datetime import timedelta, datetime
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET = "change-me"
ALGO = "HS256"
ACCESS_MIN=30

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_engine("sqlite:///./app.db")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str
    hashed_password: str

def get_session():
    with Session(engine) as s:
        yield s

app = FastAPI()

@app.on_event("startup")
def on_start():
    SQLModel.metadata.create_all(engine)

def create_token(sub: str):
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_MIN)
    return jwt.encode({"sub":sub,"exp":exp}, SECRET, algorithm=ALGO)

@app.post("/signup")
def signup(email:str, password:str, s: Session = Depends(get_session)):
    u = s.exec(select(User).where(User.email==email)).first()
    if u: raise HTTPException(400, "exists")
    u = User(email=email, hashed_password=pwd_ctx.hash(password))
    s.add(u); s.commit(); s.refresh(u)
    return {"id":u.id, "email":u.email}

@app.post("/login")
def login(email:str, password:str, s: Session = Depends(get_session)):
    u = s.exec(select(User).where(User.email==email)).first()
    if not u or not pwd_ctx.verify(password, u.hashed_password):
        raise HTTPException(401, "bad creds")
    return {"access_token": create_token(u.email), "token_type":"bearer"}

@app.get("/status")
def status(): return {"ok":True}
""", encoding="utf-8")
    (dest/"tests").mkdir(exist_ok=True)
    (dest/"tests"/"test_smoke.py").write_text("def test_smoke():\n    assert 2+2==4\n", encoding="utf-8")
    if req.ci: _write_ci_python(dest, req.coverage_py)

def _write_python_lib(dest: Path, req: ScaffoldApplyRequest):
    (dest/"pyproject.toml").write_text("""[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mylib"
version = "0.1.0"
description = "Biblioteca gerada pelo ToDoX"
authors = [{name="ToDoX User"}]
readme = "README.md"
requires-python = ">=3.10"
""", encoding="utf-8")
    (dest/"README.md").write_text("# mylib\n", encoding="utf-8")
    (dest/"src").mkdir(exist_ok=True)
    (dest/"src"/"mylib").mkdir(exist_ok=True)
    (dest/"src"/"mylib"/"__init__.py").write_text("__all__ = []\n", encoding="utf-8")
    (dest/"tests").mkdir(exist_ok=True)
    (dest/"tests"/"test_smoke.py").write_text("def test_smoke():\n    assert 1+1==2\n", encoding="utf-8")
    (dest/"requirements.txt").write_text("pytest\npytest-cov\n", encoding="utf-8")
    if req.ci: _write_ci_python(dest, req.coverage_py)

def _write_node_vite_react(dest: Path, req: ScaffoldApplyRequest):
    (dest/"package.json").write_text(json.dumps({
        "name":"todox-react-app","version":"0.1.0","private":True,
        "scripts":{"dev":"vite","build":"vite build","preview":"vite preview","test":"vitest run --coverage"},
        "devDependencies":{"vite":"^5.4.0","@vitejs/plugin-react":"^4.3.0","vitest":"^2.0.0","@testing-library/react":"^16.0.0","@types/node":"^20.11.0","typescript":"^5.4.0","eslint":"^9.0.0","prettier":"^3.2.0"},
        "dependencies":{"react":"^18.3.1","react-dom":"^18.3.1"}
    }, indent=2), encoding="utf-8")
    (dest/"index.html").write_text("<!doctype html>\n<div id='root'></div>\n<script type='module' src='/src/main.tsx'></script>\n", encoding="utf-8")
    (dest/"vite.config.ts").write_text("import react from '@vitejs/plugin-react'\nexport default { plugins:[react()] }\n", encoding="utf-8")
    (dest/"src").mkdir(exist_ok=True)
    (dest/"src"/"main.tsx").write_text("import React from 'react'\nimport {createRoot} from 'react-dom/client'\nconst App=()=><>Hello ToDoX</>\ncreateRoot(document.getElementById('root')!).render(<App/>)\n", encoding="utf-8")
    (dest/"vitest.config.ts").write_text(f"""import {{ defineConfig }} from 'vitest/config'
export default defineConfig({{
  test: {{
    coverage: {{ provider: 'v8', reporter: ['text','json'], thresholds: {{ lines: {req.coverage_node}, statements: {req.coverage_node} }} }}
  }}
}})
""", encoding="utf-8")
    if req.ci: _write_ci_node(dest, req.coverage_node)

def _write_node_nextjs(dest: Path, req: ScaffoldApplyRequest):
    (dest/"package.json").write_text(json.dumps({
        "name":"todox-next-app","private":True,"version":"0.1.0",
        "scripts":{"dev":"next dev","build":"next build","start":"next start","test":"vitest run --coverage"},
        "dependencies":{"next":"^14.2.10","react":"^18.3.1","react-dom":"^18.3.1"},
        "devDependencies":{"vitest":"^2.0.0","@types/node":"^20.11.0","typescript":"^5.4.0","eslint":"^9.0.0","prettier":"^3.2.0"}
    }, indent=2), encoding="utf-8")
    (dest/"next.config.js").write_text("module.exports = { reactStrictMode: true }\n", encoding="utf-8")
    os.makedirs(dest/"app", exist_ok=True)
    (dest/"app"/"page.tsx").write_text("export default function Page(){ return <main>Hello ToDoX</main>}\n", encoding="utf-8")
    (dest/"vitest.config.ts").write_text(f"""import {{ defineConfig }} from 'vitest/config'
export default defineConfig({{
  test: {{
    coverage: {{ provider: 'v8', reporter: ['text','json'], thresholds: {{ lines: {req.coverage_node}, statements: {req.coverage_node} }} }}
  }}
}})
""", encoding="utf-8")
    if req.ci: _write_ci_node(dest, req.coverage_node)

def _write_node_monorepo_pnpm(dest: Path, req: ScaffoldApplyRequest):
    (dest/"pnpm-workspace.yaml").write_text("packages:\n  - 'packages/*'\n", encoding="utf-8")
    (dest/"package.json").write_text(json.dumps({"name":"todox-monorepo","private":True,"version":"0.1.0","scripts":{"test":"pnpm -r test"}}, indent=2), encoding="utf-8")
    # packages/app (vite react)
    app = dest/"packages"/"app"
    os.makedirs(app, exist_ok=True)
    (app/"package.json").write_text(json.dumps({
        "name":"app","private":True,"version":"0.1.0",
        "scripts":{"dev":"vite","build":"vite build","preview":"vite preview","test":"vitest run --coverage"},
        "devDependencies":{"vite":"^5.4.0","@vitejs/plugin-react":"^4.3.0","vitest":"^2.0.0","@testing-library/react":"^16.0.0","typescript":"^5.4.0"},
        "dependencies":{"react":"^18.3.1","react-dom":"^18.3.1"}
    }, indent=2), encoding="utf-8")
    os.makedirs(app/"src", exist_ok=True)
    (app/"src"/"main.tsx").write_text("export const ok=true;\n", encoding="utf-8")
    (app/"vitest.config.ts").write_text(f"export default {{ test: {{ coverage: {{ provider: 'v8', thresholds: {{ lines: {req.coverage_node} }} }} }} }}\n", encoding="utf-8")
    # packages/api (express)
    api = dest/"packages"/"api"
    os.makedirs(api, exist_ok=True)
    (api/"package.json").write_text(json.dumps({
        "name":"api","private":True,"version":"0.1.0",
        "scripts":{"start":"node index.js","test":"vitest run --coverage"},
        "devDependencies":{"vitest":"^2.0.0"},
        "dependencies":{"express":"^4.19.2"}
    }, indent=2), encoding="utf-8")
    (api/"index.js").write_text("const express=require('express'); const app=express(); app.get('/status',(req,res)=>res.json({ok:true})); app.listen(3001);\n", encoding="utf-8")
    (api/"vitest.config.ts").write_text(f"export default {{ test: {{ coverage: {{ provider: 'v8', thresholds: {{ lines: {req.coverage_node} }} }} }} }}\n", encoding="utf-8")
    if req.ci: _write_ci_pnpm_monorepo(dest)


def _write_dockerfiles(dest: Path, kind: str):
    if kind == "python":
        (dest/"Dockerfile").write_text("""FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""", encoding="utf-8")
    elif kind == "next":
        (dest/"Dockerfile").write_text("""FROM node:20-alpine as deps
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* .npmrc* ./
RUN npm ci || true
COPY . .
RUN npm run build

FROM node:20-alpine as runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app .
EXPOSE 3000
CMD ["npm","start"]
""", encoding="utf-8")

def _write_docker_ci(dest: Path):
    wf = dest/".github/workflows"; wf.mkdir(parents=True, exist_ok=True)
    (wf/"docker.yml").write_text("""name: Docker Build
on:
  push:
    branches: [ main ]
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Build (no push)
        run: |
          echo "Building images if Dockerfiles exist"
          if [ -f Dockerfile ]; then docker build -t todox-app:ci . ; fi
          if [ -f apps/api/Dockerfile ]; then docker build -t todox-api:ci apps/api ; fi
          if [ -f apps/web/Dockerfile ]; then docker build -t todox-web:ci apps/web ; fi
""", encoding="utf-8")

def _write_monorepo_next_fastapi(dest: Path, req: ScaffoldApplyRequest):
    # Root files
    (dest/"README.md").write_text("# ToDoX Monorepo (Next.js + FastAPI)\n", encoding="utf-8")
    # Workspaces (npm) minimal
    (dest/"package.json").write_text(json.dumps({
        "name":"todox-monorepo",
        "private": True,
        "workspaces": ["apps/*"]
    }, indent=2), encoding="utf-8")

    # apps/web (Next.js)
    web = dest/"apps"/"web"
    web.mkdir(parents=True, exist_ok=True)
    (web/"package.json").write_text(json.dumps({
        "name":"web","private":True,"version":"0.1.0",
        "scripts":{"dev":"next dev","build":"next build","start":"next start","test":"vitest run --coverage"},
        "dependencies":{"next":"^14.2.10","react":"^18.3.1","react-dom":"^18.3.1"},
        "devDependencies":{"vitest":"^2.0.0","@types/node":"^20.11.0","typescript":"^5.4.0","eslint":"^9.0.0","prettier":"^3.2.0"}
    }, indent=2), encoding="utf-8")
    (web/"next.config.js").write_text("module.exports = { reactStrictMode: true }\n", encoding="utf-8")
    os.makedirs(web/"app", exist_ok=True)
    (web/"app"/"page.tsx").write_text("export default function Page(){ return <main>Hello ToDoX Monorepo</main>}\n", encoding="utf-8")
    (web/"vitest.config.ts").write_text(f"""import {{ defineConfig }} from 'vitest/config'
export default defineConfig({{
  test: {{
    coverage: {{ provider: 'v8', reporter: ['text','json'], thresholds: {{ lines: {req.coverage_node}, statements: {req.coverage_node} }} }}
  }}
}})
""", encoding="utf-8")
    if req.dockerize:
        _write_dockerfiles(web, "next")

    # apps/api (FastAPI)
    api = dest/"apps"/"api"
    api.mkdir(parents=True, exist_ok=True)
    (api/"requirements.txt").write_text("fastapi\nuvicorn\npytest\npytest-cov\n", encoding="utf-8")
    os.makedirs(api/"app", exist_ok=True)
    (api/"app"/"main.py").write_text("from fastapi import FastAPI\napp=FastAPI()\n@app.get('/status')\ndef status(): return {'ok':True}\n", encoding="utf-8")
    os.makedirs(api/"tests", exist_ok=True)
    (api/"tests"/"test_smoke.py").write_text("def test_ok(): assert 3*3==9\n", encoding="utf-8")
    if req.dockerize:
        _write_dockerfiles(api, "python")

    # Compose
    if req.compose:
        (dest/"docker-compose.yml").write_text("""version: "3.9"
services:
  api:
    build: ./apps/api
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports: [ "8000:8000" ]
    volumes: [ "./apps/api:/app" ]
  web:
    build: ./apps/web
    command: npm run start
    environment: [ "NEXT_PUBLIC_API=http://localhost:8000" ]
    ports: [ "3000:3000" ]
    volumes: [ "./apps/web:/app" ]
    depends_on: [ api ]
""", encoding="utf-8")

    # CI for monorepo: reuse node CI and python CI at repo root (Docker CI too)
    _write_docker_ci(dest)

def _write_governance_files(dest: Path):
    gh = dest/".github"
    gh.mkdir(exist_ok=True)
    (gh/"CODEOWNERS").write_text("* @your-org/owners @your-handle\n", encoding="utf-8")
    docs = dest/"docs"; docs.mkdir(exist_ok=True)
    (docs/"branch_policy.md").write_text("""# Política de Proteção de Branch
- Branch padrão: `main`
- Requer PR com pelo menos 1 aprovação
- Status checks obrigatórios: CI, Lint, Coverage
- Proibir merge com cobertura < threshold
- Exigir atualização com target branch antes do merge
- Commits assinados (opcional)
""", encoding="utf-8")

from typing import Any, Dict, List

# @app.get("/tasks/{task_id}/details", response_model=TaskDetailsOut)
# def get_task_details(task_id: int, db: Session = Depends(get_db)):
#     # TaskDetails model not implemented yet
#     return {"error": "TaskDetails not implemented"}

# @app.patch("/tasks/{task_id}/details", response_model=TaskDetailsOut)
# def patch_task_details(task_id: int, payload: TaskDetailsUpdate, db: Session = Depends(get_db)):
#     # TaskDetails model not implemented yet
#     return {"error": "TaskDetails not implemented"}

# ZIP (download) scaffold-only
@app.get("/projects/{project_id}/scaffold")
def scaffold_project(project_id: int, db: Session = Depends(get_db)):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        tasks_yaml = _build_tasks_yaml(db, project_id)
        # Basic ToDox + VSCode
        z.writestr(".gitignore", ".venv/\n__pycache__/\nnode_modules/\n.env\n")
        z.writestr(".editorconfig", "root = true\n[*]\ncharset = utf-8\nend_of_line = lf\ninsert_final_newline = true\nindent_style = space\nindent_size = 2\n")
        vscode_json = {
            "version":"2.0.0",
            "tasks":[
                {"label":"ToDox: listar","type":"shell","command":"python todox/todoctl.py list"},
                {"label":"ToDox: próxima elegível","type":"shell","command":"python todox/todoctl.py next"},
                {"label":"ToDox: iniciar (IN_PROGRESS)","type":"shell","command":"python todox/todoctl.py start ${input:taskId}"},
                {"label":"ToDox: finalizar (DONE)","type":"shell","command":"python todox/todoctl.py finish ${input:taskId}"},
                {"label":"ToDox: reordenar","type":"shell","command":"python todox/todoctl.py reorder ${input:taskId} ${input:newOrder}"}
            ],
            "inputs":[
                {"id":"taskId","type":"promptString","description":"ID da tarefa (ex.: T-001)"},
                {"id":"newOrder","type":"promptString","description":"Nova ordem (ex.: 15)"}
            ]
        }
        z.writestr(".vscode/tasks.json", json.dumps(vscode_json, ensure_ascii=False, indent=2))
        z.writestr("todox/TASKS.yaml", tasks_yaml)
        z.writestr("todox/DOD.md", "# Definition of Done (DoD)\n- lint_ok\n- tests_pass\n- unit_coverage>=80\n- contract_test_ok\n- readme_badge\n")
        z.writestr("todox/PROMPT_CARD.md", "# SOP — Operação de Agente ToDox\n(consulte o painel ToDoX para instruções)\n")
        z.writestr("todox/RUNS/.keep", "")
        z.writestr("todox/SESSIONS/.keep", "")
        z.writestr("todox/todoctl.py", '#!/usr/bin/env python3\nprint("todoctl minimal — instale a versão completa do ToDoX CLI")\n')
        z.writestr("README_TODOX.md", "Estrutura gerada automaticamente pelo ToDoX.\n")
    buf.seek(0)
    headers = {"Content-Disposition": f"attachment; filename=project_{project_id}_scaffold.zip"}
    return StreamingResponse(buf, media_type="application/zip", headers=headers)

# APPLY (server-side create + optional init)
@app.post("/projects/{project_id}/scaffold/apply")
def scaffold_apply(project_id: int, req: ScaffoldApplyRequest, db: Session = Depends(get_db)):
    dest = Path(os.path.expanduser(req.dest_path)).resolve()
    if SAFE_SCAFFOLD_ROOT:
        safe = Path(SAFE_SCAFFOLD_ROOT).resolve()
        if not str(dest).startswith(str(safe)):
            raise HTTPException(400, f"dest_path deve estar sob {safe}")
    if dest.exists() and any(dest.iterdir()):
        raise HTTPException(400, "dest_path já existe e não está vazio")
    os.makedirs(dest, exist_ok=True)

    tasks_yaml = _build_tasks_yaml(db, project_id)
    _write_common(dest, tasks_yaml)
    _write_code_quality(dest, req)

    # Template content
    if req.template == "python-fastapi":
        _write_python_fastapi(dest, req)
    elif req.template == "python-fastapi-sqlmodel-jwt":
        _write_python_fastapi_sqlmodel_jwt(dest, req)
    elif req.template == "python-lib":
        _write_python_lib(dest, req)
    elif req.template == "node-vite-react":
        _write_node_vite_react(dest, req)
    elif req.template == "node-nextjs":
        _write_node_nextjs(dest, req)
    elif req.template == "node-monorepo-pnpm":
        _write_node_monorepo_pnpm(dest, req)
    elif req.template == "monorepo-next-fastapi":
        _write_monorepo_next_fastapi(dest, req)

    logs = []
    def run(cmd, cwd=None):
        try:
            p = subprocess.run(cmd, cwd=cwd or dest, capture_output=True, text=True, shell=os.name=="nt")
            logs.append({ "cmd": cmd if isinstance(cmd,str) else ' '.join(cmd), "code": p.returncode, "out": p.stdout, "err": p.stderr })
            return p.returncode == 0
        except Exception as e:
            logs.append({ "cmd": str(cmd), "code": -1, "out": "", "err": str(e) })
            return False

    # Git init + first commit
    if req.init_git:
        run(["git","init"])
        run(["git","add","-A"])
        run(["git","commit","-m", req.pr_title or "chore: scaffold inicial ToDoX"])

    # Install deps
    if req.install_deps:
        # Python
        if (dest/"requirements.txt").exists():
            pip = "pip"
            pip_path = (dest/".venv/Scripts/pip.exe") if os.name=="nt" else (dest/".venv/bin/pip")
            if (dest/".venv").exists() and os.path.exists(pip_path):
                pip = str(pip_path)
            run([pip, "install", "-r", "requirements.txt"])
        # Node (npm)
        if (dest/"package.json").exists():
            run(["npm","install"])
        # pnpm monorepo
        if (dest/"pnpm-workspace.yaml").exists():
            run(["pnpm","install"])
        # Go
        if (dest/"go.mod").exists():
            run(["go","mod","tidy"])

    # Remote repo & PR (GitHub via gh)
    if req.create_remote and req.remote_provider == "github":
        repo_name = req.repo_name or dest.name
        vis_flag = "--private" if req.remote_visibility != "public" else "--public"
        run(["gh","repo","create", repo_name, vis_flag, "--source",".", "--push"])
        if req.open_pr:
            run(["git","checkout","-b","scaffold"])
            run(["git","push","-u","origin","scaffold"])
            run(["gh","pr","create","--title", req.pr_title or "Scaffold inicial ToDoX", "--body", req.pr_body or ""])

    return JSONResponse({"ok": True, "dest": str(dest), "logs": logs})

# -------- Templates list --------
@app.get("/scaffold/templates", response_model=List[ScaffoldTemplate])
def list_scaffold_templates():
    return [
        {"key":"python-fastapi","label":"Python + FastAPI","description":"API mínima com FastAPI e pytest"},
        {"key":"python-fastapi-sqlmodel-jwt","label":"Python + FastAPI + SQLModel + JWT","description":"API com auth mínima e SQLModel"},
        {"key":"python-lib","label":"Python + Library","description":"Pacote Python (pyproject) com pytest"},
        {"key":"node-vite-react","label":"Node + Vite + React","description":"SPA com Vite/React e Vitest"},
        {"key":"node-nextjs","label":"Node + Next.js","description":"App Next.js 14 mínima com Vitest"},
        {"key":"node-monorepo-pnpm","label":"Monorepo pnpm (app+api)","description":"Workspace com Vite React e Express"},
        {"key":"go-cli","label":"Go + CLI","description":"Aplicação CLI com testes"},
        {"key":"monorepo-next-fastapi","label":"Monorepo Next.js + FastAPI","description":"Next 14 + API FastAPI com Docker & Compose"}
    ]

# -------- Export/Import YAML --------
@app.get("/projects/{project_id}/tasks/export-yaml")
def export_yaml(project_id: int, db: Session = Depends(get_db)):
    tasks_yaml = _build_tasks_yaml(db, project_id)
    return StreamingResponse(io.BytesIO(tasks_yaml.encode("utf-8")), media_type="text/yaml",
                             headers={"Content-Disposition": f"attachment; filename=project_{project_id}_tasks.yaml"})

@app.post("/projects/{project_id}/tasks/import-yaml")
async def import_yaml(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read().decode("utf-8")
    data = yaml.safe_load(content)
    if not data or "tasks" not in data:
        raise HTTPException(400, "YAML inválido")
    existing = { t.id: t for t in db.scalars(select(models.Task).where(models.Task.project_id==project_id)).all() }
    def parse_tid(s):
        m = re.match(r"T-(\d+)", str(s))
        return int(m.group(1)) if m else None
    yaml_id_to_db = {}
    for entry in data["tasks"]:
        tid = parse_tid(entry.get("id"))
        title = entry.get("title") or "Sem título"
        desc = entry.get("description") or ""
        order = int(entry.get("order") or 1000000)
        prio_str = (entry.get("priority") or "P3").upper().replace("P","")
        try: prio = int(prio_str)
        except: prio = 3
        if tid and tid in existing:
            t = existing[tid]
            t.title = title; t.description_md = desc; t.order_index = order; t.priority = prio
            db.add(t)
            yaml_id_to_db[tid] = t.id
        else:
            t = models.Task(project_id=project_id, title=title, description_md=desc, order_index=order, priority=prio)
            db.add(t); db.flush()
            yaml_id_to_db[tid or t.id] = t.id
    db.commit()
    # dependencies
    for entry in data["tasks"]:
        tid = parse_tid(entry.get("id"))
        dbid = yaml_id_to_db.get(tid)
        if not dbid: continue
        db.query(models.TaskDependency).filter(models.TaskDependency.task_id==dbid).delete()
        deps = entry.get("depends_on") or []
        if isinstance(deps, str):
            deps = [x.strip() for x in deps.split(",") if x.strip()]
        for dep in deps:
            dep_id = parse_tid(dep)
            if dep_id and yaml_id_to_db.get(dep_id):
                db.add(models.TaskDependency(task_id=dbid, depends_on_task_id=yaml_id_to_db[dep_id]))
    db.commit()
    return {"ok": True, "count": len(data["tasks"])}

# -------- Watcher (YAML sync) --------
def _watch_yaml(project_id: int, repo_path: Path, yaml_rel: str, stop_event: threading.Event):
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if stop_event.is_set(): return
            try:
                target = repo_path / yaml_rel
                if not target.exists(): return
                with target.open("rb") as f:
                    content = f.read()
                # evite loop se mudança veio do próprio export
                w = WATCHERS.get(project_id, {})
                h = hashlib.sha256(content).hexdigest()
                if w.get("last_export_hash") and w["last_export_hash"] == h:
                    return
                time.sleep(0.2)
                from fastapi.testclient import TestClient
                client = TestClient(app)
                files = {"file": ("TASKS.yaml", content, "text/yaml")}
                client.post(f"/projects/{project_id}/tasks/import-yaml", files=files)
                w["last_file_hash"] = h
            except Exception as e:
                print("Watcher import error:", e, flush=True)

    observer = Observer()
    handler = Handler()
    observer.schedule(handler, str((repo_path / yaml_rel).parent), recursive=False)
    observer.start()
    try:
        while not stop_event.is_set():
            time.sleep(0.25)
    finally:
        observer.stop()
        observer.join()

@app.post("/projects/{project_id}/watcher/start")
async def watcher_start(project_id: int, repo_path: str, yaml_relpath: str = "todox/TASKS.yaml"):
    if project_id in WATCHERS:
        raise HTTPException(400, "Watcher já em execução para este projeto")
    p = Path(os.path.expanduser(repo_path)).resolve()
    if not p.exists():
        raise HTTPException(400, "repo_path não existe")
    stop_event = threading.Event()
    th = threading.Thread(target=_watch_yaml, args=(project_id, p, yaml_relpath, stop_event), daemon=True)
    WATCHERS[project_id] = {"thread": th, "path": str(p), "yaml_rel": yaml_relpath, "stop": stop_event, "last_file_hash": None, "last_export_hash": None}
    th.start()
    await _emit(project_id, "watcher.started", {"path": str(p), "yaml_rel": yaml_relpath})
    return {"ok": True}

@app.post("/projects/{project_id}/watcher/stop")
async def watcher_stop(project_id: int):
    w = WATCHERS.get(project_id)
    if not w: return {"ok": True, "message": "Watcher não estava ativo"}
    w["stop"].set()
    WATCHERS.pop(project_id, None)
    await _emit(project_id, "watcher.stopped", {})
    return {"ok": True}

@app.get("/projects/{project_id}/watcher/status")
def watcher_status(project_id: int):
    w = WATCHERS.get(project_id)
    if not w: return {"active": False}
    alive = w["thread"].is_alive()
    return {"active": alive, "path": w["path"], "yaml_rel": w["yaml_rel"]}

# -------- Seed (demo) --------
@app.post("/seed")
def seed(db: Session = Depends(get_db)):
    name = "Projeto Demo"
    proj = db.scalar(select(models.Project).where(models.Project.name==name))
    if not proj:
        proj = models.Project(name=name)
        db.add(proj); db.commit(); db.refresh(proj)
    if db.scalar(select(models.Agent).where(models.Agent.name=="Agente 1")) is None:
        db.add_all([models.Agent(name="Agente 1"), models.Agent(name="Agente 2")]); db.commit()
    if not db.scalar(select(models.Task).where(models.Task.project_id==proj.id)):
        titles = [
            "Configurar repositório e CI",
            "Criar endpoint GET /status",
            "Implementar claim-next",
            "UI: listar tarefas e criar nova",
            "Worker: executar tarefa e gerar PR simulado"
        ]
        order = 10
        for t in titles:
            task = models.Task(project_id=proj.id, title=t, priority=3, order_index=order)
            order += 10
            db.add(task)
        db.commit()
    return {"ok": True, "project_id": proj.id}
