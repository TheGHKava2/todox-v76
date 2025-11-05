"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function PRs(){
  const { data } = useQuery({ queryKey:["prs"], queryFn: api.prs.list, refetchInterval: 4000 });
  return (
    <div className="panel">
      <h2 className="text-lg mb-2">PRs simulados</h2>
      <table className="table">
        <thead><tr><th>ID</th><th>Run</th><th>Título</th><th>Resumo Diff</th><th>Criado</th></tr></thead>
        <tbody>
          {data?.map((p:any)=>(
            <tr key={p.id}>
              <td>{p.id}</td><td>{p.task_run_id}</td><td>{p.title}</td>
              <td><pre className="whitespace-pre-wrap">{(p.diff_summary||"").slice(0,160)}</pre></td>
              <td>{new Date(p.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
