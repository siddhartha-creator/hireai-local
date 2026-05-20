"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { RecruiterInterviewsView } from "@/features/dashboard/ResourceListViews";

export default function RecruiterInterviewsPage() {
  return (
    <ProtectedPage role="recruiter">
      <RecruiterInterviewsView />
    </ProtectedPage>
  );
}
