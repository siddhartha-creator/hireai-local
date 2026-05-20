import { apiClient } from "@/lib/api/client";
import type { LoginPayload, RegisterPayload, TokenResponse, UserRead } from "@/types/api";

export function login(payload: LoginPayload) {
  return apiClient<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function register(payload: RegisterPayload) {
  return apiClient<UserRead>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getCurrentUser(token: string) {
  return apiClient<UserRead>("/auth/me", { token });
}
