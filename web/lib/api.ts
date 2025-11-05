export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function j<T=any>(url: string, init?: RequestInit): Promise<T>{
  const r = await fetch(url, { ...(init||{}), headers: { "Content-Type": "application/json", ...(init?.headers||{}) } });
  if(!r.ok){
    throw new Error(await r.text());
  }
  const ct = r.headers.get("content-type") || "";
  if(ct.includes("application/json")) return r.json();
  // @ts-ignore
  return r.text();
}

export const api = {
  projects: {
    list: () => j(`${API_BASE}/projects`),
    create: (name: string) => j(`${API_BASE}/projects`, { method: "POST", body: JSON.stringify({ name }) }),
  },
  tasks: {
    list: (projectId: number) => j(`${API_BASE}/projects/${projectId}/tasks`),
    create: (projectId: number, title: string, priority=3) => j(`${API_BASE}/projects/${projectId}/tasks`, { method: "POST", body: JSON.stringify({ title, priority, description_md: "" }) }),
    reorder: (taskId: number, newOrder: number) => j(`${API_BASE}/tasks/${taskId}/reorder?new_order_index=${newOrder}`, { method: "PATCH" }),
    details: {
      get: (taskId: number) => j(`${API_BASE}/tasks/${taskId}/details`),
      patch: (taskId: number, payload: any) => j(`${API_BASE}/tasks/${taskId}/details`, { method: "PATCH", body: JSON.stringify(payload) }),
    },
  },
  prs: { list: () => j(`${API_BASE}/pull-requests`) },
  seed: () => j(`${API_BASE}/seed`, { method: "POST" }),
  templates: () => j(`${API_BASE}/scaffold/templates`),
  scaffoldZip: (projectId: number) => `${API_BASE}/projects/${projectId}/scaffold`,
  applyScaffold: (projectId: number, payload: any) => j(`${API_BASE}/projects/${projectId}/scaffold/apply`, { method: "POST", body: JSON.stringify(payload) }),
  yaml: {
    export: (projectId: number) => `${API_BASE}/projects/${projectId}/tasks/export-yaml`,
    import: (projectId: number, file: File) => {
      const fd = new FormData(); fd.append("file", file);
      return fetch(`${API_BASE}/projects/${projectId}/tasks/import-yaml`, { method: "POST", body: fd }).then(r => r.json());
    },
  },
  watcher: {
    start: (projectId: number, repo: string, rel="todox/TASKS.yaml") => j(`${API_BASE}/projects/${projectId}/watcher/start?repo_path=${encodeURIComponent(repo)}&yaml_relpath=${encodeURIComponent(rel)}`, { method:"POST" }),
    stop: (projectId: number) => j(`${API_BASE}/projects/${projectId}/watcher/stop`, { method:"POST" }),
    status: (projectId: number) => j(`${API_BASE}/projects/${projectId}/watcher/status`),
  }
};
