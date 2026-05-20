import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { LoginForm } from "@/features/auth/AuthForm";
import { AuthProvider } from "@/stores/AuthContext";

const router = {
  push: vi.fn(),
  replace: vi.fn(),
};

vi.mock("next/navigation", () => ({
  useRouter: () => router,
  usePathname: () => "/candidate/dashboard",
}));

describe("auth flow", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.localStorage.clear();
  });

  it("logs in and stores the token", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          access_token: "test-token",
          token_type: "bearer",
          user: {
            id: "user-id",
            email: "candidate@example.com",
            full_name: "Candidate User",
            is_active: true,
            roles: [{ id: "role-id", name: "candidate" }],
          },
        }),
      }),
    );

    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>,
    );

    fireEvent.change(screen.getByPlaceholderText("Email"), { target: { value: "candidate@example.com" } });
    fireEvent.change(screen.getByPlaceholderText("Password"), { target: { value: "Password123!" } });
    fireEvent.click(screen.getByRole("button", { name: "Login" }));

    await waitFor(() => expect(window.localStorage.getItem("hireai.accessToken")).toBe("test-token"));
    expect(router.push).toHaveBeenCalledWith("/candidate/dashboard");
  });

  it("redirects protected pages when no user is authenticated", async () => {
    render(
      <AuthProvider>
        <ProtectedPage role="candidate">
          <div>Private</div>
        </ProtectedPage>
      </AuthProvider>,
    );

    await waitFor(() => expect(router.replace).toHaveBeenCalledWith("/login"));
  });
});
