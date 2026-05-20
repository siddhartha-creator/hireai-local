import { apiClient } from "@/lib/api/client";

export function getCandidateProfile(token: string) {
  return apiClient<Record<string, unknown>>("/candidates/me", { token });
}

export function getRecruiterProfile(token: string) {
  return apiClient<Record<string, unknown>>("/recruiters/me", { token });
}
