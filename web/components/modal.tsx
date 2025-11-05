"use client";
import React from "react";
import cls from "classnames";

export function Modal({ open, onClose, children, title }:{ open:boolean; onClose:()=>void; children:React.ReactNode; title?:string }){
  if(!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60" onClick={onClose}></div>
      <div className={cls("relative bg-panel border border-border rounded-2xl p-4 w-[880px] max-w-[95vw] max-h-[85vh] overflow-auto")}>
        {title && <div className="text-lg font-semibold mb-2">{title}</div>}
        {children}
      </div>
    </div>
  );
}
