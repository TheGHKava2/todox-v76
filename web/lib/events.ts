"use client";
import { API_BASE } from "@/lib/api";
import { qc } from "@/lib/query";

export function attachRealtime(projectId: number){
  // Prefer WebSocket; fallback para SSE
  let closed = false;
  let cleanup: (() => void) | null = null;
  
  try{
    const ws = new WebSocket(`${API_BASE.replace('http','ws')}/ws/events?project_id=${projectId}`);
    ws.onmessage = (ev) => {
      try{
        const data = JSON.parse(ev.data || "{}");
        if(!data?.type) return;
        switch(data.type){
          case "task.created":
          case "task.reordered":
          case "task.finished":
          case "yaml.imported":
            qc.invalidateQueries({ queryKey: ["tasks", projectId] });
            qc.invalidateQueries({ queryKey: ["prs"] });
            break;
        }
      }catch{}
    };
    ws.onclose = () => { if(!closed) setTimeout(()=>attachRealtime(projectId), 1500); };
    cleanup = () => { closed = true; ws.close(); };
  }catch(_){
    // SSE fallback
    const es = new EventSource(`${API_BASE}/events/stream?project_id=${projectId}`);
    es.onmessage = (ev) => {
      try{
        const data = JSON.parse(ev.data || "{}");
        if(!data?.type) return;
        switch(data.type){
          case "task.created":
          case "task.reordered":
          case "task.finished":
          case "yaml.imported":
            qc.invalidateQueries({ queryKey: ["tasks", projectId] });
            qc.invalidateQueries({ queryKey: ["prs"] });
            break;
        }
      }catch{}
    };
    es.onerror = () => {};
    cleanup = () => es.close();
  }
  
  return cleanup || (() => {});
}
