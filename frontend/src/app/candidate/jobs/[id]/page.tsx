"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { CandidateJobDetailView } from "@/features/demo/DemoFlowViews";

export default function CandidateJobDetailPage({ params }: { params: { id: string } }) {
  return (
    <ProtectedPage role="candidate">
      <CandidateJobDetailView jobId={params.id} />
    </ProtectedPage>
  );
}
