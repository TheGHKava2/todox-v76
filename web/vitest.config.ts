import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    exclude: [
      "**/node_modules/**",
      "**/dist/**",
      "**/.next/**",
      "**/tests/e2e.spec.ts",
      "**/tests/board_backlog.spec.ts",
      "**/*.spec.ts", // Excluir arquivos .spec.ts (Playwright)
      "**/playwright/**",
    ],
    include: ["**/tests/**/*.test.ts", "**/tests/**/*.test.tsx"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "lcov"],
      thresholds: { lines: 70, functions: 70, statements: 70, branches: 60 },
    },
  },
});
