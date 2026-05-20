"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { ProfileView } from "@/features/dashboard/ResourceListViews";

export default function CandidateProfilePage() {
  return (
    <ProtectedPage role="candidate">
      <ProfileView role="candidate" />
    </ProtectedPage>
  );
}
