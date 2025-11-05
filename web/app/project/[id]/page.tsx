"use client";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams, useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button, Badge } from "@/components/ui";
import { Modal } from "@/components/modal";

type KV = Record<string,string>;

export default function ProjectView(){
  const params = useParams<{id:string}>();
  const projectId = parseInt(String(params.id||"1"));
  const { data: tasks, refetch } = useQuery({ queryKey:["tasks", projectId], queryFn: ()=>api.tasks.list(projectId), refetchInterval: 2500 });
  const [openId, setOpenId] = useState<number|null>(null);
  const [form, setForm] = useState<any>({ objective:"", scope:"", requirements_md:"", parameters:{} as KV, rules_md:"", relations:[] as string[] });
  const current = useMemo(()=> (tasks||[]).find((t:any)=>t.id===openId), [tasks, openId]);

  useEffect(()=>{
    if(openId){
      api.tasks.details.get(openId).then(d=> setForm({
        objective: d.objective||"", scope: d.scope||"", requirements_md: d.requirements_md||"",
        parameters: d.parameters||{}, rules_md: d.rules_md||"", relations: d.relations||[]
      }));
    }
  }, [openId]);

  function setParam(k:string,v:string){
    setForm((f:any)=>({ ...f, parameters: { ...(f.parameters||{}), [k]: v } }));
  }
  function delParam(k:string){
    setForm((f:any)=>{ const p={...(f.parameters||{})}; delete p[k]; return { ...f, parameters: p }; });
  }
  async function save(){
    if(!openId) return;
    await api.tasks.details.patch(openId, form);
    setOpenId(null);
    refetch();
  }

  return (
    <div className="grid gap-4">
      <header className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Projeto #{projectId}</h1>
        <div className="flex gap-2">
          <Button onClick={()=>refetch()}>Atualizar</Button>
        </div>
      </header>

      {/* Lista estilo Todoist (aproximação) */}
      <div className="panel">
        <ul className="grid gap-2">
          {(tasks||[]).map((t:any)=> (
            <li key={t.id} className="flex items-start gap-3 px-2 py-2 rounded hover:bg-[#0f1622]">
              <button className="w-5 h-5 rounded-full border border-border mt-0.5" title="Concluir"></button>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <div className="font-medium">{t.title}</div>
                  <Badge>P{t.priority}</Badge>
                  <span className="text-xs opacity-70">T-{String(t.id).padStart(3,"0")}</span>
                </div>
                {t.description_md && <div className="text-sm opacity-80 mt-1 line-clamp-2">{t.description_md}</div>}
              </div>
              <Button onClick={()=>setOpenId(t.id)}>Detalhes</Button>
            </li>
          ))}
        </ul>
      </div>

      <Modal open={!!openId} onClose={()=>setOpenId(null)} title={current? `Detalhes • ${current.title}` : "Detalhes da tarefa"}>
        <div className="grid grid-cols-2 gap-3">
          <label className="grid gap-1">
            <span className="text-sm opacity-80">Objetivo</span>
            <input className="input" value={form.objective||""} onChange={e=>setForm({...form, objective:e.target.value})}/>
          </label>
          <label className="grid gap-1">
            <span className="text-sm opacity-80">Escopo</span>
            <input className="input" value={form.scope||""} onChange={e=>setForm({...form, scope:e.target.value})}/>
          </label>
          <label className="col-span-2 grid gap-1">
            <span className="text-sm opacity-80">Requisitos (Markdown)</span>
            <textarea className="input min-h-[120px]" value={form.requirements_md||""} onChange={e=>setForm({...form, requirements_md:e.target.value})}/>
          </label>
          <label className="col-span-2 grid gap-1">
            <span className="text-sm opacity-80">Regras (Markdown)</span>
            <textarea className="input min-h-[120px]" value={form.rules_md||""} onChange={e=>setForm({...form, rules_md:e.target.value})}/>
          </label>
          <div className="col-span-2 grid gap-2">
            <div className="text-sm opacity-80">Parâmetros</div>
            <div className="grid gap-2">
              {Object.entries(form.parameters||{}).map(([k,v]:[string,any])=> (
                <div key={k} className="flex gap-2">
                  <input className="input flex-1" value={k} onChange={e=>{ const nv=e.target.value; const val=(form.parameters||{})[k]; delParam(k); setParam(nv, val); }}/>
                  <input className="input flex-1" value={String(v)} onChange={e=>setParam(k, e.target.value)}/>
                  <button className="btn" onClick={()=>delParam(k)}>Remover</button>
                </div>
              ))}
              <div className="flex gap-2">
                <input className="input flex-1" placeholder="nova_chave" onKeyDown={e=>{
                  if(e.key==='Enter'){ const k=(e.target as HTMLInputElement).value.trim(); if(k){ setParam(k, ""); (e.target as HTMLInputElement).value=""; } }
                }} />
                <span className="text-sm opacity-60 self-center">↵ para adicionar</span>
              </div>
            </div>
          </div>
          <label className="col-span-2 grid gap-1">
            <span className="text-sm opacity-80">Inter-relações (IDs ex.: T-001, T-002)</span>
            <input className="input" value={(form.relations||[]).join(", ")} onChange={e=>{
              const arr = e.target.value.split(/[,\s]+/).filter(Boolean);
              setForm({...form, relations: arr});
            }}/>
          </label>
        </div>
        <div className="flex justify-end gap-2 mt-4">
          <Button onClick={()=>setOpenId(null)}>Cancelar</Button>
          <Button onClick={save}>Salvar</Button>
        </div>
      </Modal>
    </div>
  );
}
