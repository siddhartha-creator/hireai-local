import React from "react";

export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <section className={`rounded-md border border-slate-200 bg-white p-5 ${className}`}>{children}</section>;
}

export function Badge({ children }: { children: React.ReactNode }) {
  return <span className="inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">{children}</span>;
}

export function Alert({ children }: { children: React.ReactNode }) {
  return <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">{children}</div>;
}
