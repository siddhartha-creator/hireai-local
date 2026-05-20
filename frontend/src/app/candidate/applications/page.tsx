"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { ApplicationsView } from "@/features/dashboard/ResourceListViews";

export default function CandidateApplicationsPage() {
  return (
    <ProtectedPage role="candidate">
      <ApplicationsView />
    </ProtectedPage>
  );
}
