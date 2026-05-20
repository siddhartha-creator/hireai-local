"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { CandidateResumesView } from "@/features/demo/DemoFlowViews";

export default function CandidateResumesPage() {
  return (
    <ProtectedPage role="candidate">
      <CandidateResumesView />
    </ProtectedPage>
  );
}
