"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";
import { useAuth } from "@/stores/AuthContext";
import type { UserRole } from "@/types/api";

const navItems: Record<UserRole, Array<{ href: string; label: string }>> = {
  candidate: [
    { href: "/candidate/dashboard", label: "Dashboard" },
    { href: "/candidate/jobs", label: "Jobs" },
    { href: "/candidate/applications", label: "Applications" },
    { href: "/candidate/resumes", label: "Resumes" },
    { href: "/candidate/interviews", label: "Interviews" },
    { href: "/candidate/profile", label: "Profile" },
  ],
  recruiter: [
    { href: "/recruiter/dashboard", label: "Dashboard" },
    { href: "/recruiter/jobs", label: "Jobs" },
    { href: "/recruiter/applications", label: "Applications" },
    { href: "/recruiter/interviews", label: "Interviews" },
    { href: "/recruiter/profile", label: "Profile" },
  ],
  admin: [{ href: "/admin/dashboard", label: "Dashboard" }],
};

export function AppShell({ children, role }: { children: React.ReactNode; role: UserRole }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-100 text-slate-950">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white p-5 md:block">
        <Link className="text-lg font-semibold" href="/">
          HireAI Local
        </Link>
        <nav className="mt-8 space-y-1">
          {navItems[role].map((item) => (
            <Link
              className={`block rounded-md px-3 py-2 text-sm ${
                pathname === item.href ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
              }`}
              href={item.href}
              key={item.href}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <div className="md:pl-64">
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-5">
          <div>
            <p className="text-sm font-medium">{user?.full_name ?? "Account"}</p>
            <p className="text-xs text-slate-500">{role}</p>
          </div>
          <button className="rounded-md border border-slate-300 px-3 py-2 text-sm hover:bg-slate-50" onClick={logout}>
            Logout
          </button>
        </header>
        <main className="mx-auto max-w-6xl p-5">{children}</main>
      </div>
    </div>
  );
}
