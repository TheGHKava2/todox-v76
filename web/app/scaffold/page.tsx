"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui";


function deburr(input: string): string {
  try {
    return input.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  } catch { return input; }
}
const RESERVED_WIN = new Set(["CON","PRN","AUX","NUL","COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","LPT1","LPT2","LPT3","LPT4","LPT5","LPT6","LPT7","LPT8","LPT9"]);
const INVALID = /[<>:"/\\|?*\x00-\x1F]/g;

function sanitizeNtfsSegment(s: string, maxlen=200): string {
  if(!s) return "Projeto";
  s = deburr(s).trim().replace(INVALID, " ");
  s = s.replace(/\s+/g, " ").replace(/[\. ]+$/, "");
  if(!s) s = "Projeto";
  s = s.slice(0, maxlen).trim();
  if(RESERVED_WIN.has(s.toUpperCase())) s = `_${s}_`;
  return s;
}
function zeroPad(id: number, pad=7): string {
  const x = String(id);
  return x.length >= pad ? x : ("0".repeat(pad - x.length) + x);
}
function joinWindows(base: string, seg: string): string {
  // garante barra invertida única
  if(!base) base = "E:\\";
  if(!base.endsWith("\\") && !base.endsWith("/")) {
    base += "\\";
  }
  return (base.replace(/[\/]+$/,"") + "\\" + seg).replace(/\\\\+/g,"\\");
}
function truncateForMaxPath(base: string, dirname: string, maxPath=200, extra=40): string {
  const full = joinWindows(base, dirname);
  if(full.length + extra <= maxPath) return dirname;
  const parts = dirname.split(" - ");
  if(parts.length >= 2){
    const prefix = parts[0] + " - ";
    const rest = parts.slice(1).join(" - ");
    const budget = Math.max(10, maxPath - (joinWindows(base, prefix).length) - extra);
    let trunc = rest.slice(0, budget).replace(/[\. ]+$/,"");
    return prefix + trunc;
  }
  return dirname.slice(0, Math.max(10, maxPath - base.length - extra));
}

export default function Scaffold(){
  const [templates, setTemplates] = useState<any[]>([]);
  const [projectId, setProjectId] = useState<number>(1);
  const [projects, setProjects] = useState<any[]>([]);
  const [payload, setPayload] = useState<any>({
    dest_path: "",
    template: "python-fastapi",
    init_git: true,
    create_venv: false,
    install_deps: false,
    post_init_cmd: null,
    ci: true,
    license: "MIT",
    create_remote: false,
    remote_provider: "github",
    remote_visibility: "private",
    repo_name: null,
    open_pr: false,
    pr_title: "Scaffold inicial ToDoX",
    pr_body: "",
    coverage_py: 80,
    coverage_node: 80,
    dockerize: true,
    compose: true
  });
  const [log, setLog] = useState<string>("");

// Preview do destino
const proj = projects.find((p:any)=>p.id===projectId) || projects[0];
const basePath = (payload.base_path && payload.base_path.trim()) ? payload.base_path.trim() : "E:\\";
const projName = sanitizeNtfsSegment(proj?.name || "Projeto");
const dirnameRaw = `${zeroPad(proj?.id || projectId, 7)} - ${projName}`;
const dirname = truncateForMaxPath(basePath, dirnameRaw, 200, 40);
const previewPath = payload.auto_dest ? (basePath.replace(/[\/]+$/,'') + "\\" + dirname) : payload.dest_path;


  useEffect(()=>{ api.templates().then(setTemplates); api.projects.list().then(setProjects); },[]);

  function set<K extends keyof typeof payload>(key: K, value: any){
    setPayload((p:any)=>({ ...p, [key]: value }));
  }

  async function apply(){
    setLog("Executando...");
    try{
      const res = await api.applyScaffold(projectId, payload);
      setLog(JSON.stringify(res, null, 2));
    }catch(e:any){
      setLog(e.message || String(e));
    }
  }

  return (
    <div className="grid gap-4">
      <div className="panel grid gap-2">
        <div className="grid grid-cols-2 gap-2">
          <label>Projeto
            <select className="input" value={projectId} onChange={e=>setProjectId(parseInt(e.target.value))}>
              {projects.map(p=>(<option key={p.id} value={p.id}>{p.name} (#{p.id})</option>))}
            </select>
          </label>
          <label>Template
            <select className="input" value={payload.template} onChange={e=>set("template", e.target.value)}>
              {templates.map(t=>(<option key={t.key} value={t.key}>{t.label}</option>))}
            </select>
          </label>
          <label><input type="checkbox" checked={payload.auto_dest} onChange={e=>set("auto_dest", e.target.checked)}/> Destino automático</label>
          <label>Base path (ex.: E:\\)</label>
          <input className="input" placeholder="E:\\" value={payload.base_path||""} onChange={e=>set("base_path", e.target.value||"")}/>
          <label>Destino
            <input className="input" placeholder="~/Projetos/meu-projeto" value={payload.dest_path} onChange={e=>set("dest_path", e.target.value)} disabled={payload.auto_dest}/>
          </label>
          <label>git init <input type="checkbox" checked={payload.init_git} onChange={e=>set("init_git", e.target.checked)}/></label>
          <label>venv <input type="checkbox" checked={payload.create_venv} onChange={e=>set("create_venv", e.target.checked)}/></label>
          <label>instalar deps <input type="checkbox" checked={payload.install_deps} onChange={e=>set("install_deps", e.target.checked)}/></label>
          <label>CI <input type="checkbox" checked={payload.ci} onChange={e=>set("ci", e.target.checked)}/></label>
          <label>Dockerfiles <input type="checkbox" checked={payload.dockerize} onChange={e=>set("dockerize", e.target.checked)}/></label>
          <label>docker-compose <input type="checkbox" checked={payload.compose} onChange={e=>set("compose", e.target.checked)}/></label>
          <label>License
            <select className="input" value={payload.license} onChange={e=>set("license", e.target.value)}><option>MIT</option></select>
          </label>
          <label>Py cov%
            <input className="input" type="number" min={0} max={100} value={payload.coverage_py} onChange={e=>set("coverage_py", parseInt(e.target.value||"80"))}/>
          </label>
          <label>Node cov%
            <input className="input" type="number" min={0} max={100} value={payload.coverage_node} onChange={e=>set("coverage_node", parseInt(e.target.value||"80"))}/>
          </label>
          <label>post_init_cmd
            <input className="input" value={payload.post_init_cmd||""} onChange={e=>set("post_init_cmd", e.target.value||null)}/>
          </label>
        </div>

        <details className="panel">
          <summary>Repositório remoto / PR</summary>
          <div className="grid grid-cols-2 gap-2 mt-2">
            <label><input type="checkbox" checked={payload.create_remote} onChange={e=>set("create_remote", e.target.checked)}/> criar remoto (gh)</label>
            <label>repo_name <input className="input" value={payload.repo_name||""} onChange={e=>set("repo_name", e.target.value||null)}/></label>
            <label>visibilidade
              <select className="input" value={payload.remote_visibility} onChange={e=>set("remote_visibility", e.target.value)}>
                <option value="private">private</option>
                <option value="public">public</option>
              </select>
            </label>
            <label><input type="checkbox" checked={payload.open_pr} onChange={e=>set("open_pr", e.target.checked)}/> abrir PR inicial</label>
            <label>PR title <input className="input" value={payload.pr_title||""} onChange={e=>set("pr_title", e.target.value||null)}/></label>
            <label>PR body <input className="input" value={payload.pr_body||""} onChange={e=>set("pr_body", e.target.value||null)}/></label>
          </div>
        </details>

        <div className="panel"><div className="text-sm opacity-80">Preview de destino</div><div className="text-xs break-all">{previewPath || "—"}</div><div className="text-[11px] opacity-60 mt-1">* Se a pasta existir, o ToDoX criará automaticamente &quot; - (2)&quot;.</div></div>
        <div className="flex gap-2">
          <a className="btn" href={api.scaffoldZip(projectId)} target="_blank">Baixar ZIP</a>
          <Button onClick={apply}>Gerar em {previewPath || "—"}</Button>
        </div>
      </div>
      <pre className="panel whitespace-pre-wrap">{log}</pre>
    </div>
  );
}
