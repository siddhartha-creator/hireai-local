"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { CandidateApplicationDetailView } from "@/features/demo/DemoFlowViews";

export default function CandidateApplicationDetailPage({ params }: { params: { id: string } }) {
  return (
    <ProtectedPage role="candidate">
      <CandidateApplicationDetailView applicationId={params.id} />
    </ProtectedPage>
  );
}
