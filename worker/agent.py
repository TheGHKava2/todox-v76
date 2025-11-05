import time, argparse, requests, hashlib, os
from pathlib import Path
from datetime import datetime

def sha256_of_text(t): 
    import hashlib
    return hashlib.sha256(t.encode()).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--api", default="http://localhost:8000")
    p.add_argument("--project", type=int, default=1)
    p.add_argument("--agent-id", type=int, default=1)
    p.add_argument("--artifacts-dir", default="./artifacts")
    args = p.parse_args()
    Path(args.artifacts_dir).mkdir(parents=True, exist_ok=True)
    while True:
        r = requests.post(f"{args.api}/projects/{args.project}/claim-next", json={"agent_id": args.agent_id}, timeout=10)
        data = r.json()
        task = data.get("task"); run_id = data.get("run_id")
        if not task: time.sleep(2); continue
        task_id = task["id"]
        now = datetime.utcnow().isoformat()
        content = f"# Execução da tarefa {task_id}\nAgente: {args.agent_id}\nIniciado: {now}\nResumo: Execução simulada.\n"
        path = os.path.join(args.artifacts_dir, f"task_{task_id}_agent_{args.agent_id}.md")
        with open(path, "w", encoding="utf-8") as f: f.write(content)
        h = sha256_of_text(content)
        payload = {"run_id": run_id, "status": "SUCCESS", "summary_md": "ok", "artifacts":[{"type":"file","uri":path,"hash":h,"metadata_json":{"agent":args.agent_id}}], "create_pr": True}
        requests.post(f"{args.api}/tasks/{task_id}/finish", json=payload, timeout=10)
        time.sleep(1)

if __name__ == "__main__":
    main()
