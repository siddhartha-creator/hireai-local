"use client";

import { useRouter } from "next/navigation";
import React, { FormEvent, useState } from "react";
import { register as registerRequest } from "@/features/auth/api";
import { useAuth } from "@/stores/AuthContext";
import type { UserRole } from "@/types/api";

function dashboardForRole(role: UserRole) {
  if (role === "admin") return "/admin/dashboard";
  if (role === "recruiter") return "/recruiter/dashboard";
  return "/candidate/dashboard";
}

export function LoginForm() {
  const router = useRouter();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const form = new FormData(event.currentTarget);
    try {
      const user = await login({
        email: String(form.get("email")),
        password: String(form.get("password")),
      });
      router.push(dashboardForRole(user.roles[0]?.name ?? "candidate"));
    } catch {
      setError("Login failed. Check your email and password.");
    }
  }

  return (
    <form className="space-y-4" onSubmit={onSubmit}>
      <input className="w-full rounded-md border border-slate-300 px-3 py-2" name="email" placeholder="Email" type="email" required />
      <input className="w-full rounded-md border border-slate-300 px-3 py-2" name="password" placeholder="Password" type="password" required />
      {error ? <p className="text-sm text-red-700">{error}</p> : null}
      <button className="w-full rounded-md bg-slate-900 px-4 py-2 text-white" type="submit">
        Login
      </button>
    </form>
  );
}

export function RegisterForm() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const form = new FormData(event.currentTarget);
    try {
      await registerRequest({
        email: String(form.get("email")),
        full_name: String(form.get("full_name")),
        password: String(form.get("password")),
        role: String(form.get("role")) as UserRole,
      });
      router.push("/login");
    } catch {
      setError("Registration failed. The email may already be registered.");
    }
  }

  return (
    <form className="space-y-4" onSubmit={onSubmit}>
      <input className="w-full rounded-md border border-slate-300 px-3 py-2" name="full_name" placeholder="Full name" required />
      <input className="w-full rounded-md border border-slate-300 px-3 py-2" name="email" placeholder="Email" type="email" required />
      <input className="w-full rounded-md border border-slate-300 px-3 py-2" name="password" placeholder="Password" type="password" required />
      <select className="w-full rounded-md border border-slate-300 px-3 py-2" name="role" defaultValue="candidate">
        <option value="candidate">Candidate</option>
        <option value="recruiter">Recruiter</option>
      </select>
      {error ? <p className="text-sm text-red-700">{error}</p> : null}
      <button className="w-full rounded-md bg-slate-900 px-4 py-2 text-white" type="submit">
        Register
      </button>
    </form>
  );
}
