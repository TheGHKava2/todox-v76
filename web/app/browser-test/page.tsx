"use client";

import { useState } from "react";

export default function BrowserTestPage() {
  const [results, setResults] = useState<string[]>([]);

  const addResult = (message: string) => {
    setResults((prev) => [
      ...prev,
      `${new Date().toLocaleTimeString()}: ${message}`,
    ]);
  };

  const testFetch = async () => {
    setResults([]);

    // Test 1: Direct localhost:8000
    try {
      addResult("🔄 Testing fetch to http://localhost:8000/health...");
      const response = await fetch("http://localhost:8000/health", {
        method: "GET",
        mode: "cors",
        headers: { Accept: "application/json" },
      });

      if (response.ok) {
        const data = await response.json();
        addResult(`✅ localhost:8000/health SUCCESS: ${JSON.stringify(data)}`);
      } else {
        addResult(
          `❌ localhost:8000/health failed with status: ${response.status} ${response.statusText}`
        );
      }
    } catch (error) {
      addResult(
        `❌ localhost:8000/health FETCH ERROR: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }

    // Test 2: Direct 127.0.0.1:8000
    try {
      addResult("🔄 Testing fetch to http://127.0.0.1:8000/health...");
      const response = await fetch("http://127.0.0.1:8000/health", {
        method: "GET",
        mode: "cors",
        headers: { Accept: "application/json" },
      });

      if (response.ok) {
        const data = await response.json();
        addResult(`✅ 127.0.0.1:8000/health SUCCESS: ${JSON.stringify(data)}`);
      } else {
        addResult(
          `❌ 127.0.0.1:8000/health failed with status: ${response.status} ${response.statusText}`
        );
      }
    } catch (error) {
      addResult(
        `❌ 127.0.0.1:8000/health FETCH ERROR: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }

    // Test 3: Different approach - no CORS mode
    try {
      addResult("🔄 Testing fetch without CORS mode...");
      const response = await fetch("http://localhost:8000/health", {
        method: "GET",
        headers: { Accept: "application/json" },
      });

      if (response.ok) {
        const data = await response.json();
        addResult(`✅ NO CORS MODE SUCCESS: ${JSON.stringify(data)}`);
      } else {
        addResult(
          `❌ NO CORS MODE failed with status: ${response.status} ${response.statusText}`
        );
      }
    } catch (error) {
      addResult(
        `❌ NO CORS MODE FETCH ERROR: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }

    // Test 4: Test projects endpoint
    try {
      addResult("🔄 Testing projects endpoint...");
      const response = await fetch("http://localhost:8000/projects", {
        method: "GET",
        mode: "cors",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        addResult(`✅ PROJECTS SUCCESS: Found ${data.length} projects`);
      } else {
        addResult(
          `❌ PROJECTS failed with status: ${response.status} ${response.statusText}`
        );
      }
    } catch (error) {
      addResult(
        `❌ PROJECTS FETCH ERROR: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    }
  };

  const testXMLHttp = async () => {
    addResult("🔄 Testing with XMLHttpRequest...");

    return new Promise<void>((resolve) => {
      const xhr = new XMLHttpRequest();
      xhr.open("GET", "http://localhost:8000/health", true);
      xhr.setRequestHeader("Accept", "application/json");

      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            addResult(`✅ XMLHttpRequest SUCCESS: ${xhr.responseText}`);
          } else {
            addResult(
              `❌ XMLHttpRequest failed: ${xhr.status} ${xhr.statusText}`
            );
          }
          resolve();
        }
      };

      xhr.onerror = function () {
        addResult(`❌ XMLHttpRequest ERROR: Network error`);
        resolve();
      };

      xhr.send();
    });
  };

  return (
    <div
      style={{ padding: "20px", fontFamily: "monospace", maxWidth: "800px" }}
    >
      <h1>🧪 Browser Network Test</h1>

      <div style={{ marginBottom: "20px" }}>
        <button
          onClick={testFetch}
          style={{
            padding: "10px 20px",
            marginRight: "10px",
            backgroundColor: "#007acc",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          🔄 Test Fetch API
        </button>

        <button
          onClick={testXMLHttp}
          style={{
            padding: "10px 20px",
            backgroundColor: "#28a745",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          🔄 Test XMLHttpRequest
        </button>
      </div>

      <div
        style={{
          backgroundColor: "#f8f9fa",
          border: "1px solid #dee2e6",
          borderRadius: "4px",
          padding: "15px",
          minHeight: "200px",
          fontFamily: "Consolas, monospace",
          fontSize: "12px",
          whiteSpace: "pre-wrap",
        }}
      >
        <h3>📋 Test Results:</h3>
        {results.length === 0 ? (
          <p style={{ color: "#6c757d" }}>Click a button to run tests...</p>
        ) : (
          results.map((result, index) => (
            <div
              key={index}
              style={{
                padding: "4px 0",
                borderBottom:
                  index < results.length - 1 ? "1px solid #dee2e6" : "none",
              }}
            >
              {result}
            </div>
          ))
        )}
      </div>

      <div
        style={{
          marginTop: "20px",
          padding: "10px",
          backgroundColor: "#e7f3ff",
          borderRadius: "4px",
        }}
      >
        <p>
          <strong>💡 Current Page URL:</strong>{" "}
          {typeof window !== "undefined" ? window.location.href : "Unknown"}
        </p>
        <p>
          <strong>🌐 User Agent:</strong>{" "}
          {typeof window !== "undefined"
            ? window.navigator.userAgent
            : "Unknown"}
        </p>
      </div>
    </div>
  );
}
