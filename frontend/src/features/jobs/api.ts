import { apiClient } from "@/lib/api/client";
import type { JobListItem } from "@/types/api";

export function listJobs(token: string) {
  return apiClient<JobListItem[]>("/jobs", { token });
}
