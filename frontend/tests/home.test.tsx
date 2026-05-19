import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HomePage from "@/app/page";

describe("HomePage", () => {
  it("renders project name", () => {
    render(<HomePage />);

    expect(screen.getByText("HireAI Local")).toBeInTheDocument();
  });
});
