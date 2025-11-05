from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    DONE = "DONE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    capabilities = Column(JSON, default=list)
    max_concurrency = Column(Integer, default=1)
    policy_json = Column(JSON, default=dict)
    last_heartbeat = Column(DateTime(timezone=True))

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    description_md = Column(Text, default="")
    priority = Column(Integer, default=3)  # 1=highest
    order_index = Column(Integer, index=True, default=1000000)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, index=True)
    assignee = Column(String(200), nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="tasks")
    dependencies = relationship("TaskDependency", back_populates="task", cascade="all, delete-orphan", foreign_keys="TaskDependency.task_id")
    dependents = relationship("TaskDependency", back_populates="depends_on", cascade="all, delete-orphan", foreign_keys="TaskDependency.depends_on_task_id")
    runs = relationship("TaskRun", back_populates="task", cascade="all, delete-orphan")

class TaskDependency(Base):
    __tablename__ = "task_dependencies"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), index=True)
    depends_on_task_id = Column(Integer, ForeignKey("tasks.id"), index=True)
    task = relationship("Task", foreign_keys=[task_id], back_populates="dependencies")
    depends_on = relationship("Task", foreign_keys=[depends_on_task_id], back_populates="dependents")

class TaskRun(Base):
    __tablename__ = "task_runs"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), index=True, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30), default="RUNNING")  # RUNNING/SUCCESS/FAILED/BLOCKED/RETRY
    exit_code = Column(Integer, default=0)
    summary_md = Column(Text, default="")
    log_ptr = Column(String(500), default="")
    artifacts_ptr = Column(String(500), default="")
    commit_sha = Column(String(80), default="")

    task = relationship("Task", back_populates="runs")
    artifacts = relationship("Artifact", back_populates="task_run", cascade="all, delete-orphan")

class Artifact(Base):
    __tablename__ = "artifacts"
    id = Column(Integer, primary_key=True, index=True)
    task_run_id = Column(Integer, ForeignKey("task_runs.id"), index=True)
    type = Column(String(50), default="file")  # file|log|pr|note
    uri = Column(String(500), nullable=False)
    hash = Column(String(80), default="")
    metadata_json = Column(JSON, default=dict)
    task_run = relationship("TaskRun", back_populates="artifacts")

class PullRequest(Base):
    __tablename__ = "pull_requests"
    id = Column(Integer, primary_key=True)
    task_run_id = Column(Integer, ForeignKey("task_runs.id"), index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, default="")
    diff_summary = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
