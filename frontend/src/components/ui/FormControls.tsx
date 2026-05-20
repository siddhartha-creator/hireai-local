import React from "react";

const baseClass = "w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-slate-500";

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input className={`${baseClass} ${props.className ?? ""}`} {...props} />;
}

export function Textarea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={`${baseClass} min-h-28 ${props.className ?? ""}`} {...props} />;
}

export function Select(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={`${baseClass} ${props.className ?? ""}`} {...props} />;
}
