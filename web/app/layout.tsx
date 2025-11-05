"use client";

import "./globals.css";
import Link from "next/link";
import { QueryProvider } from "@/lib/query";
import { attachRealtime } from "@/lib/events";
import React from "react";


function LiveClient(){ 
  React.useEffect(()=>{ 
    const cleanup = attachRealtime(1); 
    return cleanup || (() => {}); 
  }, []);
  return null;
}

export default function RootLayout({ children }: { children: React.ReactNode }){
  return (
    <html lang="pt-BR">
      <body>
        <header className="border-b border-border bg-[#101722] py-4">
          <div className="container flex gap-3 items-center justify-between">
            <h1 className="text-xl font-semibold">ToDoX v5</h1>
            <nav className="flex gap-3 text-sm">
              <Link href="/">Dashboard</Link>
              <Link href="/backlog">Backlog</Link>
              <Link href="/board">Board</Link>
              <Link href="/yaml-studio">YAML Studio</Link>
              <Link href="/scaffold">Scaffold</Link>
              <Link href="/watcher">Watcher</Link>
              <Link href="/prs">PRs</Link>
            </nav>
          </div>
        </header>
        <QueryProvider>
          <main className="container my-6">{children}</main>
          <LiveClient />
        </QueryProvider>
      </body>
    </html>
  );
}
