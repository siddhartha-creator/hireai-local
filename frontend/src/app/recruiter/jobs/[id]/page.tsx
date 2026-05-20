"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { RecruiterJobDetailView } from "@/features/demo/DemoFlowViews";

export default function RecruiterJobDetailPage({ params }: { params: { id: string } }) {
  return (
    <ProtectedPage role="recruiter">
      <RecruiterJobDetailView jobId={params.id} />
    </ProtectedPage>
  );
}
