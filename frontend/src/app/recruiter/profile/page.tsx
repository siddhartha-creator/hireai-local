"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { ProfileView } from "@/features/dashboard/ResourceListViews";

export default function RecruiterProfilePage() {
  return (
    <ProtectedPage role="recruiter">
      <ProfileView role="recruiter" />
    </ProtectedPage>
  );
}
