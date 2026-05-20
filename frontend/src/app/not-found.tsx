import Link from "next/link";
import React from "react";

export default function NotFoundPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <section className="w-full max-w-md rounded-md border border-slate-200 bg-white p-6 text-center">
        <h1 className="text-2xl font-semibold">Page not found</h1>
        <p className="mt-2 text-sm text-slate-600">The page you requested does not exist in this local demo.</p>
        <Link className="mt-6 inline-block rounded-md bg-slate-900 px-4 py-2 text-sm text-white" href="/">
          Return home
        </Link>
      </section>
    </main>
  );
}
