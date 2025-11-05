"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Table, Th, Td, Button } from "@/components/ui";
import { useState, useEffect } from "react";

export default function Backlog(){
  const [projectId, setProjectId] = useState<number>(1);
  const { data: tasks, refetch } = useQuery({ queryKey:["tasks", projectId], queryFn: ()=>api.tasks.list(projectId), refetchInterval: 3000 });

  useEffect(()=>{ /* poderia carregar projetos e selecionar */ },[]);

  async function bump(id:number, order:number, delta:number){
    const newOrder = Math.max(0, order + delta);
    await api.tasks.reorder(id, newOrder);
    refetch();
  }

  const [title, setTitle] = useState("");
  const [prio, setPrio] = useState(3);
  async function addTask(){
    if(!title) return;
    await api.tasks.create(projectId, title, prio);
    setTitle(""); refetch();
  }

  return (
    <div className="grid gap-4">
      <div><a className="btn" href={`/project/${projectId}`} target="_blank" rel="noopener noreferrer">Abrir projeto</a></div>
      <div className="panel">
        <div className="flex gap-2 items-center">
          <input className="input flex-1" value={title} onChange={e=>setTitle(e.target.value)} placeholder="Título da tarefa"/>
          <input className="input w-24" type="number" min={1} max={4} value={prio} onChange={e=>setPrio(parseInt(e.target.value||'3'))}/>
          <Button onClick={addTask}>Adicionar</Button>
        </div>
      </div>
      <div className="panel overflow-auto">
        <Table>
          <thead><tr><Th>ID</Th><Th>Título</Th><Th>Prior.</Th><Th>Status</Th><Th>Assignee</Th><Th>Order</Th><Th>Ações</Th></tr></thead>
          <tbody>
            {tasks?.map((t:any)=>(
              <tr key={t.id}>
                <Td>T-{String(t.id).padStart(3,'0')}</Td>
                <Td>{t.title}</Td>
                <Td>{t.priority}</Td>
                <Td>{t.status}</Td>
                <Td>{t.assignee||""}</Td>
                <Td>{t.order_index}</Td>
                <Td className="flex gap-1">
                  <Button onClick={()=>bump(t.id, t.order_index, -11)}>↑</Button>
                  <Button onClick={()=>bump(t.id, t.order_index, 11)}>↓</Button>
                </Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>
    </div>
  );
}
