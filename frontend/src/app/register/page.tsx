import Link from "next/link";
import React from "react";
import { RegisterForm } from "@/features/auth/AuthForm";

export default function RegisterPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <section className="w-full max-w-md rounded-md border border-slate-200 bg-white p-6">
        <h1 className="text-2xl font-semibold">Register</h1>
        <p className="mt-2 text-sm text-slate-600">Create a candidate or recruiter account.</p>
        <div className="mt-6">
          <RegisterForm />
        </div>
        <p className="mt-4 text-sm text-slate-600">
          Already registered? <Link className="font-medium text-slate-950" href="/login">Login</Link>
        </p>
      </section>
    </main>
  );
}
