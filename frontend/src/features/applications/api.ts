import { apiClient } from "@/lib/api/client";
import type { ApplicationRead } from "@/types/api";

export function listMyApplications(token: string) {
  return apiClient<ApplicationRead[]>("/applications/me", { token });
}

export function listAllApplications(token: string) {
  return apiClient<ApplicationRead[]>("/applications", { token });
}
