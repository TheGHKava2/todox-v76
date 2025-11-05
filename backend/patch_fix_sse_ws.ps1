
# patch_fix_sse_ws.ps1
# Aplica correções em backend\main.py:
# - Corrige StreamingResponse (retira parêntese sobrando)
# - Garante imports: asyncio, json, StreamingResponse, WebSocket/WebSocketDisconnect
# - Insere/atualiza globais SSE_SUBSCRIBERS / WS_SUBSCRIBERS
# - Substitui _emit para publicar SSE+WS
# - Substitui o endpoint /events/stream
# - Adiciona endpoint /ws/events
# Cria backup em main.py.bak

param(
  [string]$ProjectRoot = "."
)

$ErrorActionPreference = "Stop"
$main = Join-Path $ProjectRoot "backend\main.py"
if (!(Test-Path $main)) {
  Write-Error "Arquivo não encontrado: $main"
}

$orig = Get-Content -Raw -Path $main -Encoding UTF8
Copy-Item $main "$($main).bak" -Force

function Ensure-Line {
  param([string]$content,[string]$line)
  if ($content -notmatch [regex]::Escape($line)) { return $line + "`n" + $content } else { return $content }
}

# 1) Imports
$patched = $orig
if ($patched -notmatch "import asyncio") { $patched = "import asyncio`n$patched" }
if ($patched -notmatch "`nimport json") { $patched = "import json`n$patched" }
if ($patched -notmatch "from fastapi\.responses import StreamingResponse") {
  $patched = "from fastapi.responses import StreamingResponse`n$patched"
}
if ($patched -notmatch "WebSocket, WebSocketDisconnect") {
  $patched = $patched -replace "from fastapi import FastAPI, UploadFile, File, Depends, HTTPException",
                               "from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, WebSocket, WebSocketDisconnect"
}

# 2) Globais SSE/WS (remove antigas e adiciona novas)
$patched = [regex]::Replace($patched, "SSE_SUBSCRIBERS\s*=\s*.*\n", "", "Singleline")
$patched = [regex]::Replace($patched, "WS_SUBSCRIBERS\s*=\s*.*\n", "", "Singleline")

$globals = @"
SSE_SUBSCRIBERS: dict[int, list[asyncio.Queue]] = {}
WS_SUBSCRIBERS: dict[int, list[WebSocket]] = {}
"@

if ($patched -match "app = FastAPI\(") {
  $patched = $patched -replace "app = FastAPI\(", "$globals`napp = FastAPI("
} elseif ($patched -notmatch "SSE_SUBSCRIBERS: dict") {
  $patched = "$globals`n$patched"
}

# 3) _emit
$patched = [regex]::Replace($patched, "async def _emit\([^\)]*\):[\s\S]*?(?=\n@|$)", "", "Singleline")
$emit = @"
async def _emit(project_id: int, payload: dict):
    data = json.dumps(payload, ensure_ascii=False)
    # SSE
    for q in list(SSE_SUBSCRIBERS.get(project_id, [])):
        try:
            q.put_nowait(data)
        except Exception:
            pass
    # WebSocket
    for ws in list(WS_SUBSCRIBERS.get(project_id, [])):
        try:
            await ws.send_text(data)
        except Exception:
            try:
                WS_SUBSCRIBERS.get(project_id, []).remove(ws)
            except Exception:
                pass
"@

# Inserir _emit antes do primeiro decorator
$idx = $patched.IndexOf("@app.")
if ($idx -ge 0) {
  $patched = $patched.Substring(0,$idx) + "$emit`n" + $patched.Substring($idx)
} else {
  $patched = "$patched`n$emit`n"
}

# 4) SSE endpoint
$patched = [regex]::Replace($patched, "@app\.get\(\"/events/stream\"[\s\S]*?return\s+StreamingResponse\([^\)]*\)\s*\)", "", "Singleline")
$sse = @"
@app.get("/events/stream")
async def events_stream(project_id: int):
    async def gen():
        q: asyncio.Queue = asyncio.Queue()
        SSE_SUBSCRIBERS.setdefault(project_id, []).append(q)
        try:
            while True:
                payload = await q.get()
                yield f"data: {payload}\\n\\n"
        finally:
            try:
                SSE_SUBSCRIBERS.get(project_id, []).remove(q)
            except Exception:
                pass
    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
"@
# Inserir depois de _emit
$patched = $patched -replace [regex]::Escape($emit), "$emit`n$sse`n"

# 5) WebSocket endpoint
$patched = [regex]::Replace($patched, "@app\.websocket\(\"/ws/events\"[\s\S]*?finally:[\s\S]*?\n", "", "Singleline")
$ws = @"
@app.websocket("/ws/events")
async def ws_events(websocket: WebSocket, project_id: int):
    await websocket.accept()
    WS_SUBSCRIBERS.setdefault(project_id, []).append(websocket)
    try:
        while True:
            await websocket.receive_text()  # aceita 'ping' do cliente
    except WebSocketDisconnect:
        pass
    finally:
        subs = WS_SUBSCRIBERS.get(project_id, [])
        if websocket in subs:
            subs.remove(websocket)
"@

if ($patched -notmatch "@app\.websocket\(\"/ws/events\"") {
  $patched = "$patched`n$ws`n"
}

Set-Content -Path $main -Value $patched -Encoding UTF8
Write-Host "Patch aplicado com sucesso em $main"

