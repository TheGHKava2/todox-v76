from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str

class ProjectOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description_md: str = ""
    priority: int = 3

class TaskOut(BaseModel):
    id: int
    project_id: int
    title: str
    description_md: str
    priority: int
    order_index: int
    status: str
    assignee: Optional[str] = None
    class Config:
        from_attributes = True

class AgentCreate(BaseModel):
    name: str
    capabilities: List[str] = []
    max_concurrency: int = 1

class AgentOut(BaseModel):
    id: int
    name: str
    capabilities: List[str] = []
    max_concurrency: int = 1
    class Config:
        from_attributes = True

class ClaimRequest(BaseModel):
    agent_id: int

class ClaimResponse(BaseModel):
    task: Optional[TaskOut] = None
    run_id: Optional[int] = None

class ArtifactIn(BaseModel):
    type: str = "file"
    uri: str
    hash: str = ""
    metadata_json: Any = {}

class FinishRequest(BaseModel):
    run_id: int
    status: str
    summary_md: str = ""
    artifacts: List[ArtifactIn] = []
    create_pr: bool = True
    pr_title: Optional[str] = None
    pr_description: Optional[str] = ""
    pr_diff_summary: Optional[str] = ""

class PullRequestOut(BaseModel):
    id: int
    task_run_id: int
    title: str
    description: str
    diff_summary: str
    created_at: datetime
    class Config:
        from_attributes = True

class ScaffoldApplyRequest(BaseModel):
    dest_path: str
    template: str = "python-fastapi"
    init_git: bool = True
    create_venv: bool = False
    install_deps: bool = False
    post_init_cmd: Optional[str] = None
    auto_dest: bool = False
    base_path: Optional[str] = None
    ci: bool = True
    license: str = "MIT"
    create_remote: bool = False
    remote_provider: str = "github"
    remote_visibility: str = "private"  # private|public|internal
    repo_name: Optional[str] = None
    open_pr: bool = False
    pr_title: Optional[str] = "Scaffold inicial ToDoX"
    pr_body: Optional[str] = "Este PR contém a estrutura inicial gerada pelo ToDoX."
    coverage_py: int = 80
    coverage_node: int = 80
    dockerize: bool = True
    compose: bool = True

class ScaffoldTemplate(BaseModel):
    key: str
    label: str
    description: str

class TaskDetailsOut(BaseModel):
    objective: Optional[str] = None
    scope: Optional[str] = None
    requirements_md: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    rules_md: Optional[str] = None
    relations: Optional[List[str]] = None

class TaskDetailsUpdate(BaseModel):
    objective: Optional[str] = None
    scope: Optional[str] = None
    requirements_md: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    rules_md: Optional[str] = None
    relations: Optional[List[str]] = None
