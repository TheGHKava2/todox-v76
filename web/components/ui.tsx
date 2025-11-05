import React from "react";
import cls from "classnames";

export function Button(props: React.ButtonHTMLAttributes<HTMLButtonElement> & {variant?: "primary"|"ghost"}){
  const { className, variant="primary", ...rest } = props;
  return <button className={cls("btn", variant==="ghost" && "bg-transparent hover:bg-brand/20")} {...rest} />;
}
export function Input(props: React.InputHTMLAttributes<HTMLInputElement>){ return <input className="input" {...props}/>; }
export function Select(props: React.SelectHTMLAttributes<HTMLSelectElement>){ return <select className="input" {...props}/>; }
export function Card(props: React.HTMLAttributes<HTMLDivElement>){ return <div className="panel" {...props}/>; }
export function Table(props: React.TableHTMLAttributes<HTMLTableElement>){ return <table className="table" {...props}/>; }
export function Th(props: React.ThHTMLAttributes<HTMLTableCellElement>){ return <th className="th" {...props}/>; }
export function Td(props: React.TdHTMLAttributes<HTMLTableCellElement>){ return <td className="td" {...props}/>; }
export function Badge(props: React.HTMLAttributes<HTMLSpanElement>){ return <span className="badge" {...props}/>; }
