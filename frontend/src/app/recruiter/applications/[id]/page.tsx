"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { RecruiterApplicationDetailView } from "@/features/demo/DemoFlowViews";

export default function RecruiterApplicationDetailPage({ params }: { params: { id: string } }) {
  return (
    <ProtectedPage role="recruiter">
      <RecruiterApplicationDetailView applicationId={params.id} />
    </ProtectedPage>
  );
}
