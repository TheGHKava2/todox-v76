"use client";

import { useState, useEffect } from "react";

export default function DebugPage() {
  const [tests, setTests] = useState<
    Array<{ type: string; message: string; success: boolean }>
  >([]);

  const addTest = (type: string, message: string, success: boolean) => {
    setTests((prev) => [...prev, { type, message, success }]);
  };

  const runTests = async () => {
    setTests([]);

    // Test 1: Verificar variáveis de ambiente
    addTest("ENV", `NODE_ENV: ${process.env.NODE_ENV}`, true);
    addTest(
      "ENV",
      `NEXT_PUBLIC_API_URL: ${process.env.NEXT_PUBLIC_API_URL || "undefined"}`,
      true
    );

    // Test 2: Verificar window.location
    addTest("CLIENT", `Window origin: ${window.location.origin}`, true);
    addTest("CLIENT", `Hostname: ${window.location.hostname}`, true);

    // Test 3: Testar API Base
    const getAPIBase = () => {
      if (typeof window !== "undefined") {
        if (
          window.location.hostname === "localhost" ||
          window.location.hostname === "127.0.0.1"
        ) {
          return "http://localhost:8000";
        }
        return `${window.location.protocol}//${window.location.host}/api`;
      }
      return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    };

    const apiBase = getAPIBase();
    addTest("API", `API Base: ${apiBase}`, true);

    // Test 4: Teste de conectividade
    try {
      addTest("FETCH", "Testando conexão...", true);
      const response = await fetch(`${apiBase}/projects`);

      if (response.ok) {
        const data = await response.json();
        addTest("FETCH", `✅ Conexão OK - ${data.length} projetos`, true);
      } else {
        addTest("FETCH", `❌ Status: ${response.status}`, false);
      }
    } catch (error) {
      addTest(
        "FETCH",
        `❌ Erro: ${error instanceof Error ? error.message : String(error)}`,
        false
      );
    }

    // Test 5: Teste de POST
    try {
      addTest("POST", "Testando POST...", true);
      const response = await fetch(`${apiBase}/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: `Debug Test ${Date.now()}` }),
      });

      if (response.ok) {
        const data = await response.json();
        addTest("POST", `✅ POST OK - Projeto ${data.id} criado`, true);
      } else {
        const errorText = await response.text();
        addTest(
          "POST",
          `❌ POST falhou: ${response.status} - ${errorText}`,
          false
        );
      }
    } catch (error) {
      addTest(
        "POST",
        `❌ POST erro: ${
          error instanceof Error ? error.message : String(error)
        }`,
        false
      );
    }
  };

  useEffect(() => {
    runTests();
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "monospace" }}>
      <h1>🔧 Debug Frontend ↔ Backend</h1>

      <button
        onClick={runTests}
        style={{
          padding: "10px 20px",
          margin: "10px 0",
          backgroundColor: "#007acc",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        🔄 Executar Testes
      </button>

      <div>
        {tests.map((test, index) => (
          <div
            key={index}
            style={{
              padding: "8px",
              margin: "4px 0",
              backgroundColor: test.success ? "#d4edda" : "#f8d7da",
              border: `1px solid ${test.success ? "#c3e6cb" : "#f5c6cb"}`,
              borderRadius: "4px",
            }}
          >
            <strong>[{test.type}]</strong> {test.message}
          </div>
        ))}
      </div>

      <div
        style={{
          marginTop: "20px",
          padding: "10px",
          backgroundColor: "#f8f9fa",
          borderRadius: "4px",
        }}
      >
        <h3>💡 Como testar no console:</h3>
        <pre
          style={{
            backgroundColor: "#e9ecef",
            padding: "10px",
            borderRadius: "4px",
          }}
        >
          {`// 1. Verificar objetos globais
console.log("window.api:", window.api);
console.log("API_BASE:", window.API_BASE);

// 2. Testar API diretamente
fetch('http://localhost:8000/projects').then(r => r.json()).then(console.log);

// 3. Criar projeto
window.api?.projects.create("Teste Console").then(console.log);`}
        </pre>
      </div>
    </div>
  );
}
