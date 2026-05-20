import React from "react";

export function MetricCard({ label, value, helper }: { label: string; value: number | string; helper?: string | null }) {
  return (
    <section className="rounded-md border border-slate-200 bg-white p-4">
      <p className="text-sm text-slate-600">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
      {helper ? <p className="mt-1 text-xs text-slate-500">{helper}</p> : null}
    </section>
  );
}
