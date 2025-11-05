"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

export const qc = new QueryClient();
export function QueryProvider({ children }: { children: React.ReactNode }){
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>
}
