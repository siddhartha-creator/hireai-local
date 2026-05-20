"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { CandidateInterviewDetailView } from "@/features/demo/DemoFlowViews";

export default function CandidateInterviewDetailPage({ params }: { params: { id: string } }) {
  return (
    <ProtectedPage role="candidate">
      <CandidateInterviewDetailView sessionId={params.id} />
    </ProtectedPage>
  );
}
