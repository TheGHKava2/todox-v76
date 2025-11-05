"use client";
import { useEffect, useRef, useState } from "react";
import Editor from "@monaco-editor/react";
import { api } from "@/lib/api";
import yaml from "js-yaml";
import Ajv from "ajv";
import schema from "@/lib/tasks_schema.json";
import { Button } from "@/components/ui";

export default function YAMLStudio(){
  const [projectId, setProjectId] = useState(1);
  const [text, setText] = useState<string>("");
  const [errors, setErrors] = useState<string[]>([]);
  const [result, setResult] = useState<any>(null);
  function validateCross(obj:any, push:(s:string)=>void){
    try{
      const ids = new Set<string>();
      (obj.tasks||[]).forEach((t:any)=>{ if(t.id) ids.add(t.id) });
      (obj.tasks||[]).forEach((t:any)=>{
        (t.depends_on||[]).forEach((d:string)=>{ if(!ids.has(d)) push(`Task ${t.id||'?'} depende de ID inexistente: ${d}`); });
      });
      // ciclo simples: DFS
      const graph: Record<string,string[]> = {};
      (obj.tasks||[]).forEach((t:any)=>{ graph[t.id]= (t.depends_on||[]) });
      const temp=new Set<string>(), perm=new Set<string>();
      function dfs(n:string){
        if(perm.has(n)) return false; if(temp.has(n)) return true; temp.add(n);
        for(const m of (graph[n]||[])){ if(dfs(m)) return true; }
        temp.delete(n); perm.add(n); return false;
      }
      for(const id of Object.keys(graph)){ if(dfs(id)) { push('Ciclo detectado no grafo de dependências'); break; } }
    }catch(e:any){ push('Erro em validação cruzada: '+(e.message||String(e))); }
  }

  async function load(){
    const url = api.yaml.export(projectId);
    const r = await fetch(url);
    setText(await r.text());
  }

  function validate(){
    const errs: string[] = [];
    try{
      const obj:any = yaml.load(text) || {};
      const ajv = new Ajv({ allErrors: true, strict: false });
      const validate = ajv.compile(schema as any);
      const ok = validate(obj);
      if(!ok && validate.errors){ errs.push(...validate.errors.map(e=>`${e.instancePath||'/'} ${e.message}`)); }
      validateCross(obj, (s)=>errs.push(s));
      if(!obj.tasks || !Array.isArray(obj.tasks)){ errs.push("`tasks` ausente ou não é lista"); }
      setResult(obj);
    }catch(e:any){
      errs.push(String(e.message||e));
    }
    setErrors(errs);
  }

  async function save(){
    const blob = new Blob([text], { type: "text/yaml" });
    // @ts-ignore
    blob.name = "TASKS.yaml";
    // @ts-ignore
    const file = new File([blob], "TASKS.yaml", { type: "text/yaml" });
    const res = await api.yaml.import(projectId, file);
    alert("Importado: " + JSON.stringify(res));
  }

  useEffect(()=>{ load(); },[]);

  return (
    <div className="grid gap-3">
      <div className="flex gap-2">
        <Button onClick={load}>Carregar</Button>
        <Button onClick={validate}>Validar</Button>
        <Button onClick={save}>Salvar no ToDoX</Button>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="panel">
          <Editor height="60vh" defaultLanguage="yaml" value={text} onChange={(v)=>setText(v||"")} options={{ minimap:{enabled:false} }}/>
        </div>
        <div className="grid gap-3">
          <div className="panel">
            <h3 className="font-semibold mb-2">Erros</h3>
            {errors.length? <ul className="list-disc pl-5">{errors.map((e,i)=>(<li key={i} className="text-red-300">{e}</li>))}</ul> : <p className="opacity-70 text-sm">Sem erros.</p>}
          </div>
          <div className="panel">
            <h3 className="font-semibold mb-2">Preview</h3>
            <pre className="whitespace-pre-wrap text-sm">{JSON.stringify(result, null, 2)}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}
