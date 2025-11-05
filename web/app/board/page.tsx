"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { LoadingSpinner } from "@/components/loading";

const cols = ["TODO", "IN_PROGRESS", "REVIEW", "DONE"];

export default function Board() {
  const { data: tasks, isLoading } = useQuery({
    queryKey: ["tasks", 1],
    queryFn: () => api.tasks.list(1),
    refetchInterval: 3000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner />
        <span className="ml-2">Carregando board...</span>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-4 gap-3">
      {cols.map((c) => (
        <div key={c} className="panel min-h-[400px]">
          <h3 className="font-semibold mb-2">{c}</h3>
          <div className="grid gap-2">
            {tasks
              ?.filter((t: any) => t.status === c)
              .map((t: any) => (
                <div key={t.id} className="panel border-dashed">
                  <div className="text-sm font-medium">{t.title}</div>
                  <div className="text-xs opacity-70">
                    P{t.priority} · T-{String(t.id).padStart(3, "0")}
                  </div>
                </div>
              ))}
          </div>
        </div>
      ))}
    </div>
  );
}
