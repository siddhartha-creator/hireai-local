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
  recruiter_id?: string;
  title: string;
  description?: string;
  requirements_json?: unknown;
  skills_json?: unknown;
  seniority?: string | null;
  location?: string | null;
  employment_type?: string | null;
  salary_min?: number | null;
  salary_max?: number | null;
  status: string;
  created_at: string;
  updated_at?: string;
};

export type JobCreatePayload = {
  title: string;
  description: string;
  requirements_json?: string[];
  skills_json?: string[];
  seniority?: string;
  location?: string;
  employment_type?: string;
  salary_min?: number | null;
  salary_max?: number | null;
  status: string;
};

export type ApplicationRead = {
  id: string;
  job_id: string;
  candidate_id: string;
  status: string;
  cover_letter?: string | null;
  applied_at: string;
  updated_at?: string;
};

export type ResumeListItem = {
  id: string;
  candidate_id: string;
  file_name: string;
  original_file_name: string;
  file_type: string;
  file_size: number;
  extracted_skills_json?: string[] | null;
  is_primary: boolean;
  uploaded_at: string;
  updated_at: string;
  parsed_data_json?: ParsedResumeData | null;
};

export type ParsedResumeData = {
  skills: string[];
  education: unknown[];
  experience: unknown[];
  summary: string;
  parser_version: string;
};

export type ResumeUploadResponse = {
  resume: ResumeListItem;
  parsed_data: ParsedResumeData;
};

export type MatchScoreRead = {
  id: string;
  application_id: string;
  candidate_id: string;
  job_id: string;
  overall_score: number;
  skill_score: number;
  experience_score: number;
  education_score: number;
  location_score: number;
  explanation_json: Record<string, unknown>;
  matched_skills_json: string[];
  missing_skills_json: string[];
  scoring_version: string;
  created_at: string;
  updated_at: string;
};

export type ScoreApplicationResponse = {
  score: MatchScoreRead;
  breakdown: {
    overall_score: number;
    skill_score: number;
    experience_score: number;
    education_score: number;
    location_score: number;
  };
  explanation: {
    summary: string;
    skill_reason: string;
    experience_reason: string;
    education_reason: string;
    location_reason: string;
    recommendation: string;
  };
};

export type CandidateAnswerRead = {
  id: string;
  question_id: string;
  answer_text: string;
  score?: number | null;
  feedback_json?: Record<string, unknown> | null;
  answered_at: string;
};

export type InterviewQuestionRead = {
  id: string;
  session_id: string;
  question_text: string;
  question_type: string;
  skill_tag?: string | null;
  expected_signals_json?: Record<string, unknown> | null;
  order_index: number;
  answer?: CandidateAnswerRead | null;
};

export type InterviewSessionSummary = {
  id: string;
  application_id: string;
  job_id: string;
  status: string;
  overall_score?: number | null;
  started_at: string;
};

export type InterviewSessionRead = InterviewSessionSummary & {
  candidate_id: string;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
  feedback_json?: Record<string, unknown> | null;
  questions: InterviewQuestionRead[];
};
