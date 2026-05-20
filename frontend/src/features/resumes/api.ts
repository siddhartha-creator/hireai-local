import { apiClient } from "@/lib/api/client";
import type { ParsedResumeData, ResumeListItem, ResumeUploadResponse } from "@/types/api";

export function listMyResumes(token: string) {
  return apiClient<ResumeListItem[]>("/resumes/me", { token });
}

export function uploadResume(token: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return apiClient<ResumeUploadResponse>("/resumes/upload", {
    method: "POST",
    token,
    body: formData,
  });
}

export function getParsedResume(token: string, resumeId: string) {
  return apiClient<ParsedResumeData>(`/resumes/${resumeId}/parsed`, { token });
}
