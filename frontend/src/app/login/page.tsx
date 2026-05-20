import Link from "next/link";
import React from "react";
import { LoginForm } from "@/features/auth/AuthForm";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <section className="w-full max-w-md rounded-md border border-slate-200 bg-white p-6">
        <h1 className="text-2xl font-semibold">Login</h1>
        <p className="mt-2 text-sm text-slate-600">Access your HireAI Local workspace.</p>
        <div className="mt-6">
          <LoginForm />
        </div>
        <p className="mt-4 text-sm text-slate-600">
          New here? <Link className="font-medium text-slate-950" href="/register">Create an account</Link>
        </p>
      </section>
    </main>
  );
}
