import React from "react";
import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-mist text-ink">
      <section className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6">
        <p className="mb-4 text-sm font-semibold uppercase tracking-wide text-signal">
          Local-first hiring infrastructure
        </p>
        <h1 className="text-5xl font-bold tracking-normal sm:text-6xl">HireAI Local</h1>
        <p className="mt-5 max-w-2xl text-xl text-slate-700">
          AI Interview & Hiring Platform
        </p>
        <div className="mt-8 flex gap-3">
          <Link className="rounded-md bg-slate-900 px-4 py-2 text-sm text-white" href="/login">
            Login
          </Link>
          <Link className="rounded-md border border-slate-300 px-4 py-2 text-sm" href="/register">
            Register
          </Link>
        </div>
      </section>
    </main>
  );
}
