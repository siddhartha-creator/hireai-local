"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { JobsView } from "@/features/dashboard/ResourceListViews";

export default function RecruiterJobsPage() {
  return (
    <ProtectedPage role="recruiter">
      <JobsView />
    </ProtectedPage>
  );
}
