"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/stores/AuthContext";
import type { UserRole } from "@/types/api";

export function useRequireAuth(roles?: UserRole[]) {
  const auth = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (auth.isLoading) {
      return;
    }
    if (!auth.user) {
      router.replace("/login");
      return;
    }
    if (roles?.length && !auth.hasRole(roles)) {
      router.replace("/");
    }
  }, [auth, roles, router]);

  return auth;
}
