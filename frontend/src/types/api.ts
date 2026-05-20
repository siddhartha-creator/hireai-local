export type ApiResponse<T> = {
  data: T | null;
  message: string;
  request_id?: string;
  errors?: Array<Record<string, unknown>>;
};

export type UserRole = "admin" | "recruiter" | "candidate";

export type RoleRead = {
  id: string;
  name: UserRole;
  description?: string | null;
};

export type UserRead = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  roles: RoleRead[];
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
  user: UserRead;
};

export type RegisterPayload = {
  email: string;
  full_name: string;
  password: string;
  role: UserRole;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type MetricCard = {
  label: string;
  value: number | string;
  helper_text?: string | null;
};

export type RecentActivityItem = {
  id: string;
  type: string;
  title: string;
  description?: string | null;
  occurred_at: string;
};

export type RecruiterDashboard = {
  metric_cards: MetricCard[];
  total_jobs: number;
  open_jobs: number;
  closed_jobs: number;
  total_applications: number;
  shortlisted_candidates: number;
  accepted_candidates: number;
  average_match_score: number | null;
  average_interview_score: number | null;
  top_skills_requested: Array<{ skill: string; count: number }>;
  recent_applications: RecentActivityItem[];
  activity_timeline: RecentActivityItem[];
};

export type CandidateDashboard = {
  metric_cards: MetricCard[];
  total_applications: number;
  application_status_breakdown: Array<{ status: string; count: number }>;
  average_match_score: number | null;
  average_interview_score: number | null;
  completed_interviews: number;
  pending_interviews: number;
  top_matched_skills: Array<{ skill: string; count: number }>;
  recent_applications: RecentActivityItem[];
  activity_timeline: RecentActivityItem[];
};

export type PlatformAnalytics = {
  metric_cards: MetricCard[];
  total_users: number;
  total_candidates: number;
  total_recruiters: number;
  total_jobs: number;
  total_applications: number;
  total_interviews: number;
  average_platform_match_score: number | null;
};

export type JobListItem = {
  id: string;
  title: string;
  seniority?: string | null;
  location?: string | null;
  employment_type?: string | null;
  status: string;
  created_at: string;
};

export type ApplicationRead = {
  id: string;
  job_id: string;
  candidate_id: string;
  status: string;
  cover_letter?: string | null;
  applied_at: string;
};

export type InterviewSessionSummary = {
  id: string;
  application_id: string;
  job_id: string;
  status: string;
  overall_score?: number | null;
  started_at: string;
};
