import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CandidateDashboardView } from "@/features/dashboard/DashboardViews";

vi.mock("@/stores/AuthContext", () => ({
  useAuth: () => ({ token: "test-token" }),
}));

vi.mock("@/features/analytics/api", () => ({
  getCandidateDashboard: vi.fn().mockResolvedValue({
    metric_cards: [
      { label: "Applications", value: 2 },
      { label: "Avg match score", value: 80 },
    ],
    activity_timeline: [
      {
        id: "activity-id",
        type: "application",
        title: "Application submitted",
        description: "Backend Engineer",
        occurred_at: "2026-05-20T10:00:00Z",
      },
    ],
  }),
}));

describe("CandidateDashboardView", () => {
  it("renders dashboard metrics from the API", async () => {
    render(<CandidateDashboardView />);

    await waitFor(() => expect(screen.getByText("Candidate Dashboard")).toBeInTheDocument());
    expect(screen.getByText("Applications")).toBeInTheDocument();
    expect(screen.getByText("Application submitted")).toBeInTheDocument();
  });
});
