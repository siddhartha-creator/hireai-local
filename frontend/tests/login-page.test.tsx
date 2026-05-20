import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import LoginPage from "@/app/login/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/stores/AuthContext", () => ({
  useAuth: () => ({ login: vi.fn() }),
}));

describe("LoginPage", () => {
  it("renders demo credential hints", () => {
    render(<LoginPage />);

    expect(screen.getByText("Demo accounts")).toBeInTheDocument();
    expect(screen.getByText("admin@hireai.local / Password123!")).toBeInTheDocument();
    expect(screen.getByText("recruiter@hireai.local / Password123!")).toBeInTheDocument();
    expect(screen.getByText("candidate@hireai.local / Password123!")).toBeInTheDocument();
  });
});
