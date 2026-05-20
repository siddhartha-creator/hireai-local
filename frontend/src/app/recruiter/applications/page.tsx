"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { RecruiterApplicationsView } from "@/features/dashboard/ResourceListViews";

export default function RecruiterApplicationsPage() {
  return (
    <ProtectedPage role="recruiter">
      <RecruiterApplicationsView />
    </ProtectedPage>
  );
}
