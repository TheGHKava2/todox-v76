const $ = (sel) => document.querySelector(sel);
let currentProjectId = 1;

function api() { return $("#apiUrl").value.trim(); }

async function fetchJSON(url, opts={}){
  const r = await fetch(url, opts);
  if(!r.ok){ throw new Error(await r.text()); }
  if (r.headers.get('content-type')?.includes('application/json')) return await r.json();
  return await r.text();
}

async function loadTemplates(){
  const t = await fetchJSON(api()+"/scaffold/templates");
  const sel = $("#template");
  sel.innerHTML = t.map(x=>`<option value="${x.key}">${x.label}</option>`).join('');
}

async function loadProjects(){
  const data = await fetchJSON(api()+"/projects");
  const el = $("#projects");
  el.innerHTML = data.map(p => `<button class="btn" data-id="${p.id}" onclick="selectProject(${p.id})">${p.name}</button>`).join(" ");
  if(data.length && !data.find(p=>p.id===currentProjectId)) currentProjectId = data[0].id;
  await loadTasks();
  await loadPRs();
}

async function selectProject(id){
  currentProjectId = id;
  await loadTasks();
  await loadPRs();
}

async function loadTasks(){
  const data = await fetchJSON(api()+`/projects/${currentProjectId}/tasks`);
  const tbody = $("#tasksTable tbody");
  tbody.innerHTML = data.map(t => `
    <tr>
      <td>T-${String(t.id).padStart(3,'0')}</td>
      <td>${t.title}</td>
      <td>${t.priority}</td>
      <td>${t.status}</td>
      <td>${t.assignee || ""}</td>
      <td>${t.order_index}</td>
      <td>
        <button onclick="bumpUp(${t.id}, ${t.order_index})">↑</button>
        <button onclick="bumpDown(${t.id}, ${t.order_index})">↓</button>
      </td>
    </tr>
  `).join("");
}

async function loadPRs(){
  const data = await fetchJSON(api()+"/pull-requests");
  const tbody = $("#prsTable tbody");
  tbody.innerHTML = data.map(p => `
    <tr>
      <td>${p.id}</td>
      <td>${p.task_run_id}</td>
      <td>${p.title}</td>
      <td><pre style="white-space:pre-wrap">${(p.diff_summary||"").slice(0,160)}</pre></td>
      <td>${new Date(p.created_at).toLocaleString()}</td>
    </tr>
  `).join("");
}

async function seed(){
  await fetchJSON(api()+"/seed", {method:"POST"});
  await loadProjects();
}

async function createProject(){
  const name = $("#newProject").value.trim();
  if(!name) return;
  await fetchJSON(api()+"/projects", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({name})});
  $("#newProject").value = "";
  await loadProjects();
}

async function createTask(){
  const title = $("#taskTitle").value.trim();
  const priority = parseInt($("#taskPriority").value || "3", 10);
  if(!title) return;
  await fetchJSON(api()+`/projects/${currentProjectId}/tasks`, {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({title, priority, description_md:""})});
  $("#taskTitle").value = "";
  await loadTasks();
}

async function bumpUp(id, order){
  const newOrder = Math.max(0, order - 11);
  await fetchJSON(api()+`/tasks/${id}/reorder?new_order_index=${newOrder}`, {method:"PATCH"});
  await loadTasks();
}
async function bumpDown(id, order){
  const newOrder = order + 11;
  await fetchJSON(api()+`/tasks/${id}/reorder?new_order_index=${newOrder}`, {method:"PATCH"});
  await loadTasks();
}

async function downloadScaffoldZip(){
  const url = api()+`/projects/${currentProjectId}/scaffold`;
  const r = await fetch(url);
  if(!r.ok){ alert('Falha ao gerar scaffold'); return; }
  const blob = await r.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `project_${currentProjectId}_scaffold.zip`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(()=>URL.revokeObjectURL(a.href), 3000);
}

async function applyScaffold(){
  const destPath = $("#destPath").value.trim();
  if(!destPath){ alert("Informe o caminho destino."); return; }
  const payload = {
    dest_path: destPath,
    template: $("#template").value,
    init_git: $("#initGit").checked,
    create_venv: $("#createVenv").checked,
    install_deps: $("#installDeps").checked,
    post_init_cmd: $("#postCmd").value.trim() || null,
    ci: $("#ci").checked,
    license: $("#license").value,
    create_remote: $("#createRemote").checked,
    remote_provider: "github",
    remote_visibility: $("#remoteVisibility").value,
    repo_name: $("#repoName").value.trim() || null,
    open_pr: $("#openPr").checked,
    pr_title: $("#prTitle").value.trim() || null,
    pr_body: $("#prBody").value.trim() || null,
    coverage_py: parseInt($("#covPy").value || "80", 10),
    coverage_node: parseInt($("#covNode").value || "80", 10),
    dockerize: $("#dockerize").checked,
    compose: $("#compose").checked
  };
  $("#applyLog").textContent = "Executando...";
  try{
    const res = await fetchJSON(api()+`/projects/${currentProjectId}/scaffold/apply`, {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    $("#applyLog").textContent = typeof res === 'string' ? res : JSON.stringify(res, null, 2);
  }catch(e){
    $("#applyLog").textContent = (e.message || String(e));
  }
}

async function watcherStart(){
  const repo = $("#watchRepo").value.trim();
  const rel = $("#watchRel").value.trim() || "todox/TASKS.yaml";
  const res = await fetchJSON(api()+`/projects/${currentProjectId}/watcher/start?repo_path=${encodeURIComponent(repo)}&yaml_relpath=${encodeURIComponent(rel)}`, {method:"POST"});
  $("#watchLog").textContent = JSON.stringify(res, null, 2);
}
async function watcherStop(){
  const res = await fetchJSON(api()+`/projects/${currentProjectId}/watcher/stop`, {method:"POST"});
  $("#watchLog").textContent = JSON.stringify(res, null, 2);
}
async function watcherStatus(){
  const res = await fetchJSON(api()+`/projects/${currentProjectId}/watcher/status`);
  $("#watchLog").textContent = JSON.stringify(res, null, 2);
}

async function exportYaml(){
  const url = api()+`/projects/${currentProjectId}/tasks/export-yaml`;
  const r = await fetch(url);
  if(!r.ok){ alert('Falha ao exportar'); return; }
  const blob = await r.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `project_${currentProjectId}_tasks.yaml`;
  document.body.appendChild(a);
  a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(a.href), 3000);
}

async function importYaml(){
  const f = document.querySelector('#yamlFile').files[0];
  if(!f){ alert('Selecione um arquivo YAML'); return; }
  const fd = new FormData();
  fd.append('file', f);
  const r = await fetch(api()+`/projects/${currentProjectId}/tasks/import-yaml`, { method:'POST', body: fd });
  const j = await r.json().catch(()=>({}));
  $("#yamlLog").textContent = JSON.stringify(j, null, 2);
}

$("#seedBtn").onclick = seed;
$("#reloadBtn").onclick = () => { loadProjects(); };
$("#addProject").onclick = createProject;
$("#addTask").onclick = createTask;
$("#scaffoldZipBtn").onclick = downloadScaffoldZip;
$("#applyBtn").onclick = applyScaffold;

$("#watchStart").onclick = watcherStart;
$("#watchStop").onclick = watcherStop;
$("#watchStatus").onclick = watcherStatus;

$("#exportYamlBtn").onclick = exportYaml;
$("#importYamlBtn").onclick = importYaml;

Promise.all([loadTemplates(), loadProjects()]).catch(err => console.error(err));
