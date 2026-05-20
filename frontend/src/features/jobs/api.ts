import { apiClient } from "@/lib/api/client";
import type { JobCreatePayload, JobListItem } from "@/types/api";

export function listJobs(token: string) {
  return apiClient<JobListItem[]>("/jobs", { token });
}

export function getJob(token: string, jobId: string) {
  return apiClient<JobListItem>(`/jobs/${jobId}`, { token });
}

export function createJob(token: string, payload: JobCreatePayload) {
  return apiClient<JobListItem>("/jobs", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}
