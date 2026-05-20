"use client";

import React from "react";
import { ProtectedPage } from "@/components/layout/ProtectedPage";
import { AdminDashboardView } from "@/features/dashboard/DashboardViews";

export default function AdminDashboardPage() {
  return (
    <ProtectedPage role="admin">
      <AdminDashboardView />
    </ProtectedPage>
  );
}
