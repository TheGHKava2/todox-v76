"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, Button } from "@/components/ui";
import {
  LoadingButton,
  LoadingState,
  LoadingSpinner,
} from "@/components/loading";
import { useToast } from "@/components/toast-context";
import { useState } from "react";

export default function Dashboard() {
  const toast = useToast();

  const {
    data: projects,
    refetch,
    error,
    isLoading,
  } = useQuery({
    queryKey: ["projects"],
    queryFn: api.projects.list,
    retry: 1,
    retryDelay: 1000,
  });

  const [name, setName] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const handleCreate = async () => {
    if (!name.trim()) {
      toast.warning(
        "Nome necessário",
        "Por favor, digite um nome para o projeto"
      );
      return;
    }

    setIsCreating(true);

    try {
      console.log("🚀 Criando projeto:", name);
      const result = await api.projects.create(name);
      console.log("✅ Projeto criado:", result);

      toast.success("Projeto criado!", `${name} foi criado com sucesso`);
      setName("");
      refetch();
    } catch (error) {
      console.error("❌ Erro ao criar projeto:", error);
      const errorMessage =
        error instanceof Error ? error.message : "Erro desconhecido";
      toast.error("Erro ao criar projeto", errorMessage);
    } finally {
      setIsCreating(false);
    }
  };

  if (error) {
    return (
      <div className="grid gap-4">
        <Card>
          <h2 className="text-lg mb-2 text-red-600">❌ Erro de Conexão</h2>
          <p className="text-sm text-red-500 mb-4">
            Não foi possível conectar com o backend:{" "}
            {error instanceof Error ? error.message : "Erro desconhecido"}
          </p>
          <div className="text-xs text-gray-600">
            <p>
              • Verifique se o backend está rodando em http://localhost:8000
            </p>
            <p>• Abra o console do navegador (F12) para mais detalhes</p>
            <p>• Tente recarregar a página</p>
          </div>
          <Button onClick={() => window.location.reload()} className="mt-4">
            🔄 Recarregar
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="grid gap-4">
      <Card>
        <h2 className="text-lg mb-2">Projetos</h2>
        {isLoading && (
          <div className="flex items-center gap-2 text-blue-500">
            <LoadingSpinner size="sm" />
            <span>Carregando projetos...</span>
          </div>
        )}

        <div className="flex gap-2 items-center">
          <input
            className="input flex-1"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Nome do projeto"
            disabled={isCreating}
          />
          <LoadingButton
            loading={isCreating}
            onClick={handleCreate}
            disabled={!name.trim()}
          >
            Criar
          </LoadingButton>
          <Button onClick={() => api.seed().then(() => refetch())}>
            Seed Demo
          </Button>
        </div>

        <div className="mt-3 flex gap-2 flex-wrap">
          {projects?.map((p: any) => (
            <a
              key={p.id}
              className="badge hover:underline"
              href={`/project/${p.id}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {p.name} <small className="opacity-70">#{p.id}</small>
            </a>
          ))}
        </div>

        {projects && projects.length === 0 && (
          <p className="text-gray-500 text-sm mt-2">
            Nenhum projeto encontrado. Crie o primeiro!
          </p>
        )}
      </Card>
      <Card>
        <h2 className="text-lg mb-2">Atalhos</h2>
        <p className="text-sm opacity-80">
          Use o menu acima para acessar Backlog, Board, YAML Studio, Scaffold,
          Watcher e PRs.
        </p>
      </Card>
    </div>
  );
}
