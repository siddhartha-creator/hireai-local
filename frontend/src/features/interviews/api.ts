import { apiClient } from "@/lib/api/client";
import type { CandidateAnswerRead, InterviewSessionRead, InterviewSessionSummary } from "@/types/api";

export function listMyInterviews(token: string) {
  return apiClient<InterviewSessionSummary[]>("/interviews/me", { token });
}

export function startInterview(token: string, applicationId: string) {
  return apiClient<InterviewSessionRead>("/interviews/sessions", {
    method: "POST",
    token,
    body: JSON.stringify({ application_id: applicationId }),
  });
}

export function getInterviewSession(token: string, sessionId: string) {
  return apiClient<InterviewSessionRead>(`/interviews/sessions/${sessionId}`, { token });
}

export function listApplicationInterviews(token: string, applicationId: string) {
  return apiClient<InterviewSessionSummary[]>(`/interviews/applications/${applicationId}`, { token });
}

export function answerQuestion(token: string, questionId: string, answerText: string) {
  return apiClient<CandidateAnswerRead>(`/interviews/questions/${questionId}/answer`, {
    method: "POST",
    token,
    body: JSON.stringify({ answer_text: answerText }),
  });
}

export function completeInterview(token: string, sessionId: string) {
  return apiClient<InterviewSessionRead>(`/interviews/sessions/${sessionId}/complete`, {
    method: "POST",
    token,
  });
}
