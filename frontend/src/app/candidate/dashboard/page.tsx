"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { CandidateDashboardView } from "@/features/dashboard/DashboardViews";

export default function CandidateDashboardPage() {
  return (
    <ProtectedPage role="candidate">
      <CandidateDashboardView />
    </ProtectedPage>
  );
}
