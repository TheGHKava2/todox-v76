# Testes básicos para backend ToDoX
import pytest
import requests
import json
from pathlib import Path

# Configuração base
BASE_URL = "http://127.0.0.1:8000"

class TestBackendAPI:
    """Testes básicos para a API do ToDoX"""
    
    def test_health_check(self):
        """Teste básico de saúde da API"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "ToDoX Backend"
    
    def test_get_projects(self):
        """Teste para listar projetos"""
        response = requests.get(f"{BASE_URL}/projects")
        assert response.status_code == 200
        projects = response.json()
        assert isinstance(projects, list)
    
    def test_create_project(self):
        """Teste para criar projeto"""
        import time
        timestamp = int(time.time())
        project_data = {"name": f"Projeto Teste API {timestamp}"}
        response = requests.post(
            f"{BASE_URL}/projects",
            json=project_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        project = response.json()
        assert "id" in project
        assert project["name"] == project_data["name"]
        
        # Cleanup: guardar ID para possível limpeza posterior
        if hasattr(pytest, 'created_projects'):
            pytest.created_projects.append(project["id"])
        else:
            pytest.created_projects = [project["id"]]
    
    def test_get_project_tasks(self):
        """Teste para listar tarefas de um projeto"""
        import time
        timestamp = int(time.time())
        # Primeiro criar um projeto
        project_data = {"name": f"Projeto Tasks Test {timestamp}"}
        project_response = requests.post(f"{BASE_URL}/projects", json=project_data)
        project = project_response.json()
        project_id = project["id"]
        
        # Listar tarefas do projeto
        response = requests.get(f"{BASE_URL}/projects/{project_id}/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert isinstance(tasks, list)
    
    def test_create_task(self):
        """Teste para criar tarefa"""
        import time
        timestamp = int(time.time())
        # Primeiro criar um projeto
        project_data = {"name": f"Projeto Task Creation {timestamp}"}
        project_response = requests.post(f"{BASE_URL}/projects", json=project_data)
        project = project_response.json()
        project_id = project["id"]
        
        # Criar tarefa
        task_data = {
            "title": f"Tarefa Teste {timestamp}",
            "priority": 3,
            "description_md": "Descrição de teste"
        }
        response = requests.post(
            f"{BASE_URL}/projects/{project_id}/tasks",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        task = response.json()
        assert "id" in task
        assert task["title"] == task_data["title"]
        assert task["project_id"] == project_id

# Configuração do pytest
def pytest_configure(config):
    """Configuração inicial dos testes"""
    import time
    pytest.current_timestamp = int(time.time())

def pytest_sessionstart(session):
    """Verificar se o backend está rodando antes dos testes"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            pytest.exit("Backend não está respondendo corretamente")
    except requests.exceptions.RequestException:
        pytest.exit("Backend não está rodando. Inicie o backend antes de executar os testes.")

if __name__ == "__main__":
    # Permite executar os testes diretamente
    pytest.main([__file__, "-v"])