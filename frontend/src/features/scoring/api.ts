import { apiClient } from "@/lib/api/client";
import type { MatchScoreRead, ScoreApplicationResponse } from "@/types/api";

export function scoreApplication(token: string, applicationId: string) {
  return apiClient<ScoreApplicationResponse>(`/scoring/applications/${applicationId}/score`, {
    method: "POST",
    token,
  });
}

export function getApplicationScore(token: string, applicationId: string) {
  return apiClient<MatchScoreRead>(`/scoring/applications/${applicationId}`, { token });
}

export function listJobScores(token: string, jobId: string) {
  return apiClient<MatchScoreRead[]>(`/scoring/jobs/${jobId}`, { token });
}
