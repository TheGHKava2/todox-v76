"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, Button } from "@/components/ui";
import { useState } from "react";

export default function Dashboard(){
  const { data: projects, refetch } = useQuery({ queryKey:["projects"], queryFn: api.projects.list });
  const [name, setName] = useState("Projeto Demo");
  return (
    <div className="grid gap-4">
      <Card>
        <h2 className="text-lg mb-2">Projetos</h2>
        <div className="flex gap-2 items-center">
          <input className="input flex-1" value={name} onChange={e=>setName(e.target.value)} placeholder="Nome do projeto"/>
          <Button onClick={async()=>{ await api.projects.create(name); setName(""); refetch(); }}>Criar</Button>
          <Button onClick={()=>api.seed().then(()=>refetch())}>Seed Demo</Button>
        </div>
        <div className="mt-3 flex gap-2 flex-wrap">
          {projects?.map((p:any)=>(<a key={p.id} className="badge hover:underline" href={`/project/${p.id}`} target="_blank" rel="noopener noreferrer">{p.name} <small className="opacity-70">#{p.id}</small></a>))}
        </div>
      </Card>
      <Card>
        <h2 className="text-lg mb-2">Atalhos</h2>
        <p className="text-sm opacity-80">Use o menu acima para acessar Backlog, Board, YAML Studio, Scaffold, Watcher e PRs.</p>
      </Card>
    </div>
  );
}
