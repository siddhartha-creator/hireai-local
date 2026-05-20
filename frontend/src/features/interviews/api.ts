import { apiClient } from "@/lib/api/client";
import type { InterviewSessionSummary } from "@/types/api";

export function listMyInterviews(token: string) {
  return apiClient<InterviewSessionSummary[]>("/interviews/me", { token });
}
