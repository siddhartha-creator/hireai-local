import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { JobsView } from "@/features/dashboard/ResourceListViews";
import { CandidateInterviewDetailView, CandidateResumesView } from "@/features/demo/DemoFlowViews";
import { RecruiterDashboardView } from "@/features/dashboard/DashboardViews";

vi.mock("@/stores/AuthContext", () => ({
  useAuth: () => ({
    token: "test-token",
    user: { roles: [{ name: "candidate" }] },
  }),
}));

vi.mock("@/features/jobs/api", () => ({
  listJobs: vi.fn().mockResolvedValue([
    {
      id: "job-1",
      title: "Backend Engineer",
      location: "London",
      status: "open",
      created_at: "2026-05-20T10:00:00Z",
    },
  ]),
}));

vi.mock("@/features/resumes/api", () => ({
  listMyResumes: vi.fn().mockResolvedValue([]),
  uploadResume: vi.fn(),
  getParsedResume: vi.fn(),
}));

vi.mock("@/features/interviews/api", () => ({
  getInterviewSession: vi.fn().mockResolvedValue({
    id: "session-1",
    application_id: "application-1",
    candidate_id: "candidate-1",
    job_id: "job-1",
    status: "in_progress",
    overall_score: null,
    started_at: "2026-05-20T10:00:00Z",
    created_at: "2026-05-20T10:00:00Z",
    updated_at: "2026-05-20T10:00:00Z",
    questions: [
      {
        id: "question-1",
        session_id: "session-1",
        question_text: "How have you used FastAPI?",
        question_type: "technical",
        order_index: 1,
        created_at: "2026-05-20T10:00:00Z",
      },
    ],
  }),
  answerQuestion: vi.fn(),
  completeInterview: vi.fn(),
}));

vi.mock("@/features/analytics/api", () => ({
  getRecruiterDashboard: vi.fn().mockResolvedValue({
    metric_cards: [{ label: "Total jobs", value: 1 }],
    activity_timeline: [],
  }),
}));

describe("demo pages", () => {
  it("renders recruiter dashboard", async () => {
    render(<RecruiterDashboardView />);

    await waitFor(() => expect(screen.getByText("Recruiter Dashboard")).toBeInTheDocument());
    expect(screen.getByText("Total jobs")).toBeInTheDocument();
  });

  it("renders candidate job list", async () => {
    render(<JobsView />);

    await waitFor(() => expect(screen.getByText("Backend Engineer")).toBeInTheDocument());
  });

  it("renders resume upload view", async () => {
    render(<CandidateResumesView />);

    await waitFor(() => expect(screen.getByText("Upload PDF or DOCX")).toBeInTheDocument());
  });

  it("renders interview question view", async () => {
    render(<CandidateInterviewDetailView sessionId="session-1" />);

    await waitFor(() => expect(screen.getByText(/How have you used FastAPI/)).toBeInTheDocument());
  });
});
