"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { InterviewsView } from "@/features/dashboard/ResourceListViews";

export default function CandidateInterviewsPage() {
  return (
    <ProtectedPage role="candidate">
      <InterviewsView />
    </ProtectedPage>
  );
}
