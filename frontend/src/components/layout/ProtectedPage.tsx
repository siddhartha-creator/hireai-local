"use client";

import React from "react";
import { AppShell } from "@/components/layout/AppShell";
import { LoadingState } from "@/components/ui/PageState";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import type { UserRole } from "@/types/api";

export function ProtectedPage({ role, children }: { role: UserRole; children: React.ReactNode }) {
  const { user, isLoading, hasRole } = useRequireAuth([role]);

  if (isLoading) {
    return (
      <main className="min-h-screen bg-slate-100 p-6">
        <LoadingState label="Checking session..." />
      </main>
    );
  }

  if (!user || !hasRole([role])) {
    return null;
  }

  return <AppShell role={role}>{children}</AppShell>;
}
