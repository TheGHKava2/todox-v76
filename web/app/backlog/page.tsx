"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Table, Th, Td, Button } from "@/components/ui";
import { LoadingButton, LoadingSpinner } from "@/components/loading";
import { useToast } from "@/components/toast-context";
import { useState, useEffect } from "react";

export default function Backlog() {
  const toast = useToast();
  const [projectId, setProjectId] = useState<number>(1);
  const [isAddingTask, setIsAddingTask] = useState(false);
  const [reorderingTasks, setReorderingTasks] = useState<Set<number>>(
    new Set()
  );

  const {
    data: tasks,
    refetch,
    isLoading,
  } = useQuery({
    queryKey: ["tasks", projectId],
    queryFn: () => api.tasks.list(projectId),
    refetchInterval: 3000,
  });

  useEffect(() => {
    /* poderia carregar projetos e selecionar */
  }, []);

  async function bump(id: number, order: number, delta: number) {
    const newOrder = Math.max(0, order + delta);

    setReorderingTasks((prev) => new Set(prev).add(id));

    try {
      await api.tasks.reorder(id, newOrder);
      toast.success("Tarefa reordenada", "Ordem atualizada com sucesso");
      refetch();
    } catch (error) {
      console.error("Erro ao reordenar tarefa:", error);
      toast.error(
        "Erro ao reordenar",
        "Não foi possível alterar a ordem da tarefa"
      );
    } finally {
      setReorderingTasks((prev) => {
        const newSet = new Set(prev);
        newSet.delete(id);
        return newSet;
      });
    }
  }

  const [title, setTitle] = useState("");
  const [prio, setPrio] = useState(3);
  async function addTask() {
    if (!title.trim()) {
      toast.warning(
        "Título necessário",
        "Por favor, digite um título para a tarefa"
      );
      return;
    }

    setIsAddingTask(true);

    try {
      await api.tasks.create(projectId, title, prio);
      toast.success("Tarefa criada", `"${title}" foi adicionada ao backlog`);
      setTitle("");
      refetch();
    } catch (error) {
      console.error("Erro ao criar tarefa:", error);
      toast.error(
        "Erro ao criar tarefa",
        "Não foi possível adicionar a tarefa"
      );
    } finally {
      setIsAddingTask(false);
    }
  }

  return (
    <div className="grid gap-4">
      <div>
        <a
          className="btn"
          href={`/project/${projectId}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          Abrir projeto
        </a>
      </div>
      <div className="panel">
        <div className="flex gap-2 items-center">
          <input
            className="input flex-1"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Título da tarefa"
          />
          <input
            className="input w-24"
            type="number"
            min={1}
            max={4}
            value={prio}
            onChange={(e) => setPrio(parseInt(e.target.value || "3"))}
          />
          <LoadingButton
            loading={isAddingTask}
            onClick={addTask}
            disabled={!title.trim()}
          >
            Adicionar
          </LoadingButton>
        </div>
      </div>
      <div className="panel overflow-auto">
        {isLoading ? (
          <div className="flex items-center justify-center p-8">
            <LoadingSpinner />
            <span className="ml-2">Carregando tarefas...</span>
          </div>
        ) : (
          <Table>
            <thead>
              <tr>
                <Th>ID</Th>
                <Th>Título</Th>
                <Th>Prior.</Th>
                <Th>Status</Th>
                <Th>Assignee</Th>
                <Th>Order</Th>
                <Th>Ações</Th>
              </tr>
            </thead>
            <tbody>
              {tasks?.map((t: any) => (
                <tr key={t.id}>
                  <Td>T-{String(t.id).padStart(3, "0")}</Td>
                  <Td>{t.title}</Td>
                  <Td>{t.priority}</Td>
                  <Td>{t.status}</Td>
                  <Td>{t.assignee || ""}</Td>
                  <Td>{t.order_index}</Td>
                  <Td className="flex gap-1">
                    <LoadingButton
                      loading={reorderingTasks.has(t.id)}
                      onClick={() => bump(t.id, t.order_index, -11)}
                    >
                      ↑
                    </LoadingButton>
                    <LoadingButton
                      loading={reorderingTasks.has(t.id)}
                      onClick={() => bump(t.id, t.order_index, 11)}
                    >
                      ↓
                    </LoadingButton>
                  </Td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </div>
    </div>
  );
}
