import { apiClient } from "@/lib/api/client";
import type { ApplicationRead } from "@/types/api";

export function listMyApplications(token: string) {
  return apiClient<ApplicationRead[]>("/applications/me", { token });
}

export function listAllApplications(token: string) {
  return apiClient<ApplicationRead[]>("/applications", { token });
}

export function applyToJob(token: string, jobId: string, coverLetter?: string) {
  return apiClient<ApplicationRead>("/applications", {
    method: "POST",
    token,
    body: JSON.stringify({ job_id: jobId, cover_letter: coverLetter }),
  });
}

export function getApplication(token: string, applicationId: string) {
  return apiClient<ApplicationRead>(`/applications/${applicationId}`, { token });
}

export function listApplicationsForJob(token: string, jobId: string) {
  return apiClient<ApplicationRead[]>(`/applications/job/${jobId}`, { token });
}
