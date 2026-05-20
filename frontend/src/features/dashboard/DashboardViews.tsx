"use client";

import React, { useEffect, useState } from "react";
import { MetricCard } from "@/components/ui/MetricCard";
import { DataTable } from "@/components/ui/DataTable";
import { ErrorState, LoadingState } from "@/components/ui/PageState";
import { getCandidateDashboard, getPlatformAnalytics, getRecruiterDashboard } from "@/features/analytics/api";
import { useAuth } from "@/stores/AuthContext";
import type { CandidateDashboard, PlatformAnalytics, RecentActivityItem, RecruiterDashboard } from "@/types/api";

function ActivityTable({ items }: { items: RecentActivityItem[] }) {
  return (
    <DataTable
      columns={[
        { key: "type", header: "Type", render: (item) => item.type },
        { key: "title", header: "Title", render: (item) => item.title },
        { key: "date", header: "Date", render: (item) => new Date(item.occurred_at).toLocaleString() },
      ]}
      emptyText="No recent activity yet."
      rows={items}
    />
  );
}

export function CandidateDashboardView() {
  const { token } = useAuth();
  const [data, setData] = useState<CandidateDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    getCandidateDashboard(token).then(setData).catch(() => setError("Could not load candidate dashboard."));
  }, [token]);

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState label="Loading candidate dashboard..." />;

  return <DashboardContent title="Candidate Dashboard" cards={data.metric_cards} activity={data.activity_timeline} />;
}

export function RecruiterDashboardView() {
  const { token } = useAuth();
  const [data, setData] = useState<RecruiterDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    getRecruiterDashboard(token).then(setData).catch(() => setError("Could not load recruiter dashboard."));
  }, [token]);

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState label="Loading recruiter dashboard..." />;

  return <DashboardContent title="Recruiter Dashboard" cards={data.metric_cards} activity={data.activity_timeline} />;
}

export function AdminDashboardView() {
  const { token } = useAuth();
  const [data, setData] = useState<PlatformAnalytics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    getPlatformAnalytics(token).then(setData).catch(() => setError("Could not load platform analytics."));
  }, [token]);

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState label="Loading platform analytics..." />;

  return <DashboardContent title="Admin Dashboard" cards={data.metric_cards} activity={[]} />;
}

function DashboardContent({
  title,
  cards,
  activity,
}: {
  title: string;
  cards: Array<{ label: string; value: number | string; helper_text?: string | null }>;
  activity: RecentActivityItem[];
}) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">{title}</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => (
          <MetricCard helper={card.helper_text} key={card.label} label={card.label} value={card.value} />
        ))}
      </div>
      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Recent Activity</h2>
        <ActivityTable items={activity} />
      </section>
    </div>
  );
}
