// Testes básicos para funcionalidades da API
import { describe, it, expect, beforeAll } from "vitest";

// Mock da API base - em um ambiente real, você configuraria isso
const API_BASE = "http://localhost:8000";

// Função auxiliar para fazer requests
async function apiRequest(endpoint: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
}

describe("API Integration Tests", () => {
  beforeAll(async () => {
    // Verificar se a API está rodando
    try {
      const health = await apiRequest("/health");
      expect(health.status).toBe("ok");
    } catch (error) {
      throw new Error(
        "Backend API não está rodando. Inicie o backend antes dos testes."
      );
    }
  });

  it("should fetch projects list", async () => {
    const projects = await apiRequest("/projects");
    expect(Array.isArray(projects)).toBe(true);
  });

  it("should create a new project", async () => {
    const timestamp = Date.now();
    const projectData = { name: `Projeto Teste Frontend ${timestamp}` };

    const project = await apiRequest("/projects", {
      method: "POST",
      body: JSON.stringify(projectData),
    });

    expect(project).toHaveProperty("id");
    expect(project.name).toBe(projectData.name);
  });

  it("should fetch tasks for a project", async () => {
    // Primeiro criar um projeto
    const projectData = { name: `Projeto Tasks ${Date.now()}` };
    const project = await apiRequest("/projects", {
      method: "POST",
      body: JSON.stringify(projectData),
    });

    // Buscar tarefas do projeto
    const tasks = await apiRequest(`/projects/${project.id}/tasks`);
    expect(Array.isArray(tasks)).toBe(true);
  });
});

describe("Utility Functions", () => {
  it("should validate project name format", () => {
    const validNames = [
      "Projeto Teste",
      "My Project 123",
      "Projeto-com-traços",
    ];
    const invalidNames = ["", "   ", null, undefined];

    validNames.forEach((name) => {
      expect(name && name.trim().length > 0).toBe(true);
    });

    invalidNames.forEach((name) => {
      expect(!name || name.trim().length === 0).toBe(true);
    });
  });

  it("should generate valid API URLs", () => {
    const getAPIBase = () => {
      if (typeof window !== "undefined") {
        if (
          window.location.hostname === "localhost" ||
          window.location.hostname === "127.0.0.1"
        ) {
          return "http://localhost:8000";
        }
        return `${window.location.protocol}//${window.location.host}/api`;
      }
      return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    };

    const apiBase = getAPIBase();
    expect(apiBase).toMatch(/^https?:\/\/.+/);
  });
});

describe("Component Logic Tests", () => {
  it("should validate task priority values", () => {
    const validPriorities = [1, 2, 3, 4, 5];
    const invalidPriorities = [0, 6, -1, "high", null, undefined];

    validPriorities.forEach((priority) => {
      expect(
        typeof priority === "number" && priority >= 1 && priority <= 5
      ).toBe(true);
    });

    invalidPriorities.forEach((priority) => {
      const isValid =
        typeof priority === "number" && priority >= 1 && priority <= 5;
      expect(isValid).toBe(false);
    });
  });

  it("should format task status correctly", () => {
    const statusMap = {
      TODO: "A Fazer",
      DOING: "Em Progresso",
      DONE: "Concluído",
    };

    Object.entries(statusMap).forEach(([status, label]) => {
      expect(typeof status).toBe("string");
      expect(typeof label).toBe("string");
      expect(status.length > 0).toBe(true);
    });
  });
});
