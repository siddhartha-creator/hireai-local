"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { RecruiterCreateJobView } from "@/features/demo/DemoFlowViews";

export default function RecruiterNewJobPage() {
  return (
    <ProtectedPage role="recruiter">
      <RecruiterCreateJobView />
    </ProtectedPage>
  );
}
