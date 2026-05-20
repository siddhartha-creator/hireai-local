"use client";

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, login as loginRequest } from "@/features/auth/api";
import { clearAccessToken, getAccessToken, setAccessToken } from "@/lib/auth/tokens";
import type { LoginPayload, UserRead, UserRole } from "@/types/api";

type AuthContextValue = {
  user: UserRead | null;
  token: string | null;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<UserRead>;
  logout: () => void;
  hasRole: (roles: UserRole[]) => boolean;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<UserRead | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    clearAccessToken();
    setToken(null);
    setUser(null);
    router.push("/login");
  }, [router]);

  useEffect(() => {
    const storedToken = getAccessToken();
    if (!storedToken) {
      setIsLoading(false);
      return;
    }

    setToken(storedToken);
    getCurrentUser(storedToken)
      .then(setUser)
      .catch(() => {
        clearAccessToken();
        setToken(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const response = await loginRequest(payload);
    setAccessToken(response.access_token);
    setToken(response.access_token);
    setUser(response.user);
    return response.user;
  }, []);

  const hasRole = useCallback(
    (roles: UserRole[]) => {
      const currentRoles = user?.roles.map((role) => role.name) ?? [];
      return roles.some((role) => currentRoles.includes(role));
    },
    [user],
  );

  const value = useMemo(
    () => ({ user, token, isLoading, login, logout, hasRole }),
    [user, token, isLoading, login, logout, hasRole],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return value;
}
