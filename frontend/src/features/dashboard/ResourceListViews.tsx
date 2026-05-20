"use client";

import React, { useEffect, useState } from "react";
import { DataTable } from "@/components/ui/DataTable";
import { ErrorState, LoadingState } from "@/components/ui/PageState";
import { listMyApplications } from "@/features/applications/api";
import { getRecruiterDashboard } from "@/features/analytics/api";
import { listMyInterviews } from "@/features/interviews/api";
import { listJobs } from "@/features/jobs/api";
import { getCandidateProfile, getRecruiterProfile } from "@/features/profiles/api";
import { useAuth } from "@/stores/AuthContext";
import type { ApplicationRead, InterviewSessionSummary, JobListItem, UserRole } from "@/types/api";

export function JobsView() {
  const { token } = useAuth();
  const [rows, setRows] = useState<JobListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    listJobs(token).then(setRows).catch(() => setError("Could not load jobs.")).finally(() => setLoading(false));
  }, [token]);

  if (error) return <ErrorState message={error} />;
  if (loading) return <LoadingState label="Loading jobs..." />;

  return (
    <PageBlock title="Jobs">
      <DataTable
        columns={[
          { key: "title", header: "Title", render: (job) => job.title },
          { key: "location", header: "Location", render: (job) => job.location ?? "N/A" },
          { key: "status", header: "Status", render: (job) => job.status },
        ]}
        emptyText="No jobs available."
        rows={rows}
      />
    </PageBlock>
  );
}

export function ApplicationsView() {
  const { token } = useAuth();
  const [rows, setRows] = useState<ApplicationRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    listMyApplications(token).then(setRows).catch(() => setError("Could not load applications.")).finally(() => setLoading(false));
  }, [token]);

  if (error) return <ErrorState message={error} />;
  if (loading) return <LoadingState label="Loading applications..." />;

  return (
    <PageBlock title="Applications">
      <DataTable
        columns={[
          { key: "job", header: "Job", render: (application) => application.job_id },
          { key: "status", header: "Status", render: (application) => application.status },
          { key: "date", header: "Applied", render: (application) => new Date(application.applied_at).toLocaleDateString() },
        ]}
        emptyText="No applications yet."
        rows={rows}
      />
    </PageBlock>
  );
}

export function RecruiterApplicationsView() {
  const { token } = useAuth();
  const [rows, setRows] = useState<Array<{ id: string; title: string; description?: string | null; occurred_at: string }>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    getRecruiterDashboard(token)
      .then((data) => setRows(data.recent_applications))
      .catch(() => setError("Could not load recruiter applications."))
      .finally(() => setLoading(false));
  }, [token]);

  if (error) return <ErrorState message={error} />;
  if (loading) return <LoadingState label="Loading recruiter applications..." />;

  return (
    <PageBlock title="Applications">
      <DataTable
        columns={[
          { key: "title", header: "Event", render: (item) => item.title },
          { key: "job", header: "Job", render: (item) => item.description ?? "N/A" },
          { key: "date", header: "Date", render: (item) => new Date(item.occurred_at).toLocaleDateString() },
        ]}
        emptyText="No recent applications yet."
        rows={rows}
      />
    </PageBlock>
  );
}

export function InterviewsView() {
  const { token } = useAuth();
  const [rows, setRows] = useState<InterviewSessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    listMyInterviews(token).then(setRows).catch(() => setError("Could not load interviews.")).finally(() => setLoading(false));
  }, [token]);

  if (error) return <ErrorState message={error} />;
  if (loading) return <LoadingState label="Loading interviews..." />;

  return (
    <PageBlock title="Interviews">
      <DataTable
        columns={[
          { key: "application", header: "Application", render: (session) => session.application_id },
          { key: "status", header: "Status", render: (session) => session.status },
          { key: "score", header: "Score", render: (session) => session.overall_score ?? "N/A" },
        ]}
        emptyText="No interviews yet."
        rows={rows}
      />
    </PageBlock>
  );
}

export function RecruiterInterviewsView() {
  const { token } = useAuth();
  const [rows, setRows] = useState<Array<{ id: string; type: string; title: string; description?: string | null; occurred_at: string }>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    getRecruiterDashboard(token)
      .then((data) => setRows(data.activity_timeline.filter((item) => item.type === "interview")))
      .catch(() => setError("Could not load recruiter interviews."))
      .finally(() => setLoading(false));
  }, [token]);

  if (error) return <ErrorState message={error} />;
  if (loading) return <LoadingState label="Loading recruiter interviews..." />;

  return (
    <PageBlock title="Interviews">
      <DataTable
        columns={[
          { key: "title", header: "Session", render: (item) => item.title },
          { key: "score", header: "Score", render: (item) => item.description ?? "N/A" },
          { key: "date", header: "Date", render: (item) => new Date(item.occurred_at).toLocaleDateString() },
        ]}
        emptyText="No interview activity yet."
        rows={rows}
      />
    </PageBlock>
  );
}

export function ProfileView({ role }: { role: Extract<UserRole, "candidate" | "recruiter"> }) {
  const { token } = useAuth();
  const [profile, setProfile] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    const request = role === "candidate" ? getCandidateProfile(token) : getRecruiterProfile(token);
    request.then(setProfile).catch(() => setError("Could not load profile."));
  }, [role, token]);

  if (error) return <ErrorState message={error} />;
  if (!profile) return <LoadingState label="Loading profile..." />;

  return (
    <PageBlock title="Profile">
      <pre className="overflow-auto rounded-md border border-slate-200 bg-white p-4 text-sm">{JSON.stringify(profile, null, 2)}</pre>
    </PageBlock>
  );
}

function PageBlock({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">{title}</h1>
      {children}
    </div>
  );
}
