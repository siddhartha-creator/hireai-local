"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { RecruiterDashboardView } from "@/features/dashboard/DashboardViews";

export default function RecruiterDashboardPage() {
  return (
    <ProtectedPage role="recruiter">
      <RecruiterDashboardView />
    </ProtectedPage>
  );
}
