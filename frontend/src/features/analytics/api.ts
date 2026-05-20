import { apiClient } from "@/lib/api/client";
import type { CandidateDashboard, PlatformAnalytics, RecruiterDashboard } from "@/types/api";

export function getCandidateDashboard(token: string) {
  return apiClient<CandidateDashboard>("/analytics/candidate/dashboard", { token });
}

export function getRecruiterDashboard(token: string) {
  return apiClient<RecruiterDashboard>("/analytics/recruiter/dashboard", { token });
}

export function getPlatformAnalytics(token: string) {
  return apiClient<PlatformAnalytics>("/analytics/platform", { token });
}
