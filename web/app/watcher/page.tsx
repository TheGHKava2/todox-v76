"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui";

export default function Watcher(){
  const [projectId, setProjectId] = useState(1);
  const [repo, setRepo] = useState<string>("");
  const [rel, setRel] = useState<string>("todox/TASKS.yaml");
  const [log, setLog] = useState<string>("");

  async function start(){
    const r = await api.watcher.start(projectId, repo, rel);
    setLog(JSON.stringify(r, null, 2));
  }
  async function stop(){
    const r = await api.watcher.stop(projectId);
    setLog(JSON.stringify(r, null, 2));
  }
  async function status(){
    const r = await api.watcher.status(projectId);
    setLog(JSON.stringify(r, null, 2));
  }

  return (
    <div className="panel grid gap-2">
      <div className="grid grid-cols-3 gap-2">
        <input className="input" placeholder="Caminho do repo" value={repo} onChange={e=>setRepo(e.target.value)}/>
        <input className="input" placeholder="Relpath YAML" value={rel} onChange={e=>setRel(e.target.value)}/>
        <div className="flex gap-2">
          <Button onClick={start}>Start</Button>
          <Button onClick={stop}>Stop</Button>
          <Button onClick={status}>Status</Button>
        </div>
      </div>
      <pre className="whitespace-pre-wrap">{log}</pre>
    </div>
  );
}
