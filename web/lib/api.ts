// Fallback para quando as variáveis de ambiente não estão disponíveis
const getAPIBase = () => {
  // Em desenvolvimento local
  if (typeof window !== "undefined") {
    // Cliente - verificar se estamos em localhost
    if (
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1"
    ) {
      return "http://localhost:8000";
    }
    // Em produção, usar a mesma origem com /api
    return `${window.location.protocol}//${window.location.host}/api`;
  }

  // Server-side
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
};

export const API_BASE = getAPIBase();

// Debug info
if (typeof window !== "undefined") {
  console.log("API_BASE configured as:", API_BASE);
  console.log("Environment:", process.env.NODE_ENV);
  console.log("NEXT_PUBLIC_API_URL:", process.env.NEXT_PUBLIC_API_URL);
}

export async function j<T = any>(url: string, init?: RequestInit): Promise<T> {
  console.log("🔄 API Request:", {
    url,
    method: init?.method || "GET",
    headers: init?.headers,
  });

  try {
    const r = await fetch(url, {
      ...(init || {}),
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    });

    console.log("📡 API Response:", { url, status: r.status, ok: r.ok });

    if (!r.ok) {
      const errorText = await r.text();
      console.error("❌ API Error:", {
        url,
        status: r.status,
        error: errorText,
      });
      throw new Error(errorText);
    }

    const ct = r.headers.get("content-type") || "";
    if (ct.includes("application/json")) {
      const result = await r.json();
      console.log("✅ API Success:", { url, result });
      return result;
    }

    const textResult = await r.text();
    console.log("✅ API Success (text):", { url, result: textResult });
    return textResult as T;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error("💥 API Fetch Error:", { url, error: errorMessage });
    throw error;
  }
}

export const api = {
  projects: {
    list: () => j(`${API_BASE}/projects`),
    create: (name: string) =>
      j(`${API_BASE}/projects`, {
        method: "POST",
        body: JSON.stringify({ name }),
      }),
  },
  tasks: {
    list: (projectId: number) => j(`${API_BASE}/projects/${projectId}/tasks`),
    create: (projectId: number, title: string, priority = 3) =>
      j(`${API_BASE}/projects/${projectId}/tasks`, {
        method: "POST",
        body: JSON.stringify({ title, priority, description_md: "" }),
      }),
    reorder: (taskId: number, newOrder: number) =>
      j(`${API_BASE}/tasks/${taskId}/reorder?new_order_index=${newOrder}`, {
        method: "PATCH",
      }),
    details: {
      get: (taskId: number) => j(`${API_BASE}/tasks/${taskId}/details`),
      patch: (taskId: number, payload: any) =>
        j(`${API_BASE}/tasks/${taskId}/details`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        }),
    },
  },
  prs: { list: () => j(`${API_BASE}/pull-requests`) },
  seed: () => j(`${API_BASE}/seed`, { method: "POST" }),
  templates: () => j(`${API_BASE}/scaffold/templates`),
  scaffoldZip: (projectId: number) =>
    `${API_BASE}/projects/${projectId}/scaffold`,
  applyScaffold: (projectId: number, payload: any) =>
    j(`${API_BASE}/projects/${projectId}/scaffold/apply`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  yaml: {
    export: (projectId: number) =>
      `${API_BASE}/projects/${projectId}/tasks/export-yaml`,
    import: (projectId: number, file: File) => {
      const fd = new FormData();
      fd.append("file", file);
      return fetch(`${API_BASE}/projects/${projectId}/tasks/import-yaml`, {
        method: "POST",
        body: fd,
      }).then((r) => r.json());
    },
  },
  watcher: {
    start: (projectId: number, repo: string, rel = "todox/TASKS.yaml") =>
      j(
        `${API_BASE}/projects/${projectId}/watcher/start?repo_path=${encodeURIComponent(
          repo
        )}&yaml_relpath=${encodeURIComponent(rel)}`,
        { method: "POST" }
      ),
    stop: (projectId: number) =>
      j(`${API_BASE}/projects/${projectId}/watcher/stop`, { method: "POST" }),
    status: (projectId: number) =>
      j(`${API_BASE}/projects/${projectId}/watcher/status`),
  },
};

// Expor para debugging global
if (typeof window !== "undefined") {
  (window as any).api = api;
  (window as any).API_BASE = API_BASE;
  console.log("✅ API objects exposed to window:", { api, API_BASE });
}
