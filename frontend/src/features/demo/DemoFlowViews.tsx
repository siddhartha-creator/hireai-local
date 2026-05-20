"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { FormEvent, useEffect, useState } from "react";
import { applyToJob, getApplication, listApplicationsForJob } from "@/features/applications/api";
import { answerQuestion, completeInterview, getInterviewSession, listApplicationInterviews, startInterview } from "@/features/interviews/api";
import { createJob, getJob } from "@/features/jobs/api";
import { getParsedResume, listMyResumes, uploadResume } from "@/features/resumes/api";
import { getApplicationScore, listJobScores, scoreApplication } from "@/features/scoring/api";
import { Button } from "@/components/ui/Button";
import { Alert, Badge, Card } from "@/components/ui/Card";
import { Input, Select, Textarea } from "@/components/ui/FormControls";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/PageState";
import { useAuth } from "@/stores/AuthContext";
import type {
  ApplicationRead,
  InterviewSessionRead,
  InterviewSessionSummary,
  JobListItem,
  MatchScoreRead,
  ParsedResumeData,
  ResumeListItem,
} from "@/types/api";

function useApiState<T>(loader: () => Promise<T>, deps: React.DependencyList) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError(null);
    loader()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Request failed."))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { data, setData, error, loading };
}

export function RecruiterCreateJobView() {
  const { token } = useAuth();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;
    setSaving(true);
    setError(null);
    const form = new FormData(event.currentTarget);
    try {
      const job = await createJob(token, {
        title: String(form.get("title")),
        description: String(form.get("description")),
        skills_json: String(form.get("skills")).split(",").map((skill) => skill.trim()).filter(Boolean),
        requirements_json: String(form.get("requirements")).split("\n").map((item) => item.trim()).filter(Boolean),
        seniority: String(form.get("seniority")),
        location: String(form.get("location")),
        employment_type: String(form.get("employment_type")),
        status: String(form.get("status")),
      });
      router.push(`/recruiter/jobs/${job.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create job.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Create Job</h1>
      {error ? <ErrorState message={error} /> : null}
      <Card>
        <form className="grid gap-4" onSubmit={onSubmit}>
          <Input name="title" placeholder="Job title" required />
          <Textarea name="description" placeholder="Description" required />
          <Input name="skills" placeholder="Skills, comma separated e.g. python, fastapi, docker" />
          <Textarea name="requirements" placeholder="Requirements, one per line" />
          <div className="grid gap-4 md:grid-cols-2">
            <Select name="seniority" defaultValue="mid">
              <option value="internship">Internship</option>
              <option value="junior">Junior</option>
              <option value="mid">Mid</option>
              <option value="senior">Senior</option>
              <option value="lead">Lead</option>
            </Select>
            <Input name="location" placeholder="Location" defaultValue="London" />
            <Select name="employment_type" defaultValue="full_time">
              <option value="full_time">Full time</option>
              <option value="part_time">Part time</option>
              <option value="internship">Internship</option>
              <option value="contract">Contract</option>
              <option value="remote">Remote</option>
            </Select>
            <Select name="status" defaultValue="open">
              <option value="open">Open</option>
              <option value="draft">Draft</option>
            </Select>
          </div>
          <Button disabled={saving} type="submit">{saving ? "Creating..." : "Create job"}</Button>
        </form>
      </Card>
    </div>
  );
}

export function RecruiterJobDetailView({ jobId }: { jobId: string }) {
  const { token } = useAuth();
  const jobState = useApiState(() => getJob(token!, jobId), [token, jobId]);
  const appsState = useApiState(() => listApplicationsForJob(token!, jobId), [token, jobId]);
  const scoresState = useApiState(() => listJobScores(token!, jobId).catch(() => []), [token, jobId]);

  if (jobState.loading || appsState.loading) return <LoadingState label="Loading job..." />;
  if (jobState.error) return <ErrorState message={jobState.error} />;
  if (!jobState.data) return <EmptyState message="Job not found." />;

  const scoresByApplication = new Map((scoresState.data ?? []).map((score) => [score.application_id, score]));

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">{jobState.data.title}</h1>
          <p className="mt-1 text-sm text-slate-600">{jobState.data.location ?? "No location"} · {jobState.data.status}</p>
        </div>
        <Link className="rounded-md bg-slate-900 px-4 py-2 text-sm text-white" href="/recruiter/jobs/new">New job</Link>
      </div>
      <Card>
        <p className="text-sm text-slate-700">{jobState.data.description}</p>
      </Card>
      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Applications</h2>
        <DataTable
          columns={[
            { key: "id", header: "Application", render: (app) => <Link className="font-medium text-slate-950 underline" href={`/recruiter/applications/${app.id}`}>{app.id.slice(0, 8)}</Link> },
            { key: "status", header: "Status", render: (app) => <Badge>{app.status}</Badge> },
            { key: "score", header: "Score", render: (app) => scoresByApplication.get(app.id)?.overall_score ?? "Not scored" },
          ]}
          emptyText="No applications for this job yet."
          rows={appsState.data ?? []}
        />
      </section>
    </div>
  );
}

export function RecruiterApplicationDetailView({ applicationId }: { applicationId: string }) {
  const { token } = useAuth();
  const appState = useApiState(() => getApplication(token!, applicationId), [token, applicationId]);
  const scoreState = useApiState(() => getApplicationScore(token!, applicationId).catch(() => null), [token, applicationId]);
  const interviewsState = useApiState(() => listApplicationInterviews(token!, applicationId), [token, applicationId]);
  const [message, setMessage] = useState<string | null>(null);

  async function onScore() {
    if (!token) return;
    const response = await scoreApplication(token, applicationId);
    scoreState.setData(response.score);
    setMessage("Match score recalculated.");
  }

  if (appState.loading) return <LoadingState label="Loading application..." />;
  if (appState.error) return <ErrorState message={appState.error} />;
  if (!appState.data) return <EmptyState message="Application not found." />;

  return (
    <ApplicationDetailLayout
      application={appState.data}
      interviews={interviewsState.data ?? []}
      message={message}
      onScore={onScore}
      score={scoreState.data}
      title="Recruiter Application Review"
    />
  );
}

export function CandidateJobDetailView({ jobId }: { jobId: string }) {
  const { token } = useAuth();
  const router = useRouter();
  const state = useApiState(() => getJob(token!, jobId), [token, jobId]);
  const [coverLetter, setCoverLetter] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function onApply() {
    if (!token) return;
    setError(null);
    try {
      const application = await applyToJob(token, jobId, coverLetter);
      router.push(`/candidate/applications/${application.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not apply to job.");
    }
  }

  if (state.loading) return <LoadingState label="Loading job..." />;
  if (state.error) return <ErrorState message={state.error} />;
  if (!state.data) return <EmptyState message="Job not found." />;

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-semibold">{state.data.title}</h1>
      {error ? <ErrorState message={error} /> : null}
      <Card>
        <p className="text-sm text-slate-700">{state.data.description}</p>
        <div className="mt-4 flex gap-2">
          <Badge>{state.data.status}</Badge>
          <Badge>{state.data.location ?? "Location not set"}</Badge>
        </div>
      </Card>
      <Card>
        <h2 className="mb-3 text-lg font-semibold">Apply</h2>
        <Textarea value={coverLetter} onChange={(event) => setCoverLetter(event.target.value)} placeholder="Short cover letter" />
        <Button className="mt-3" onClick={onApply}>Apply to job</Button>
      </Card>
    </div>
  );
}

export function CandidateApplicationDetailView({ applicationId }: { applicationId: string }) {
  const { token } = useAuth();
  const router = useRouter();
  const appState = useApiState(() => getApplication(token!, applicationId), [token, applicationId]);
  const scoreState = useApiState(() => getApplicationScore(token!, applicationId).catch(() => null), [token, applicationId]);
  const interviewsState = useApiState(() => listApplicationInterviews(token!, applicationId), [token, applicationId]);
  const [message, setMessage] = useState<string | null>(null);

  async function onScore() {
    if (!token) return;
    const response = await scoreApplication(token, applicationId);
    scoreState.setData(response.score);
    setMessage("Match score generated.");
  }

  async function onStartInterview() {
    if (!token) return;
    const session = await startInterview(token, applicationId);
    router.push(`/candidate/interviews/${session.id}`);
  }

  if (appState.loading) return <LoadingState label="Loading application..." />;
  if (appState.error) return <ErrorState message={appState.error} />;
  if (!appState.data) return <EmptyState message="Application not found." />;

  return (
    <ApplicationDetailLayout
      application={appState.data}
      interviews={interviewsState.data ?? []}
      message={message}
      onScore={onScore}
      onStartInterview={onStartInterview}
      score={scoreState.data}
      title="Candidate Application"
    />
  );
}

function ApplicationDetailLayout({
  application,
  interviews,
  message,
  onScore,
  onStartInterview,
  score,
  title,
}: {
  application: ApplicationRead;
  interviews: InterviewSessionSummary[];
  message: string | null;
  onScore: () => Promise<void>;
  onStartInterview?: () => Promise<void>;
  score: MatchScoreRead | null;
  title: string;
}) {
  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-semibold">{title}</h1>
      {message ? <Alert>{message}</Alert> : null}
      <Card>
        <p className="text-sm text-slate-600">Application ID</p>
        <p className="font-mono text-sm">{application.id}</p>
        <div className="mt-3"><Badge>{application.status}</Badge></div>
      </Card>
      <Card>
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold">Match Score</h2>
            <p className="text-sm text-slate-600">{score ? `Overall score ${score.overall_score}/100` : "No score generated yet."}</p>
          </div>
          <Button onClick={onScore}>{score ? "Recalculate score" : "Generate score"}</Button>
        </div>
        {score ? (
          <div className="mt-4 grid gap-2 text-sm md:grid-cols-2">
            <p>Skills: {score.skill_score}</p>
            <p>Experience: {score.experience_score}</p>
            <p>Education: {score.education_score}</p>
            <p>Location: {score.location_score}</p>
            <p className="md:col-span-2">Matched: {score.matched_skills_json.join(", ") || "None"}</p>
          </div>
        ) : null}
      </Card>
      <Card>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Interview Sessions</h2>
          {onStartInterview ? <Button onClick={onStartInterview}>Start interview</Button> : null}
        </div>
        <div className="mt-4">
          <DataTable
            columns={[
              { key: "id", header: "Session", render: (session) => <Link className="underline" href={`/candidate/interviews/${session.id}`}>{session.id.slice(0, 8)}</Link> },
              { key: "status", header: "Status", render: (session) => <Badge>{session.status}</Badge> },
              { key: "score", header: "Score", render: (session) => session.overall_score ?? "N/A" },
            ]}
            emptyText="No interview sessions yet."
            rows={interviews}
          />
        </div>
      </Card>
    </div>
  );
}

export function CandidateResumesView() {
  const { token } = useAuth();
  const resumesState = useApiState(() => listMyResumes(token!), [token]);
  const [parsed, setParsed] = useState<ParsedResumeData | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!token || !file) return;
    setError(null);
    try {
      const response = await uploadResume(token, file);
      setParsed(response.parsed_data);
      resumesState.setData([response.resume, ...(resumesState.data ?? [])]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not upload resume.");
    }
  }

  async function onParsed(resumeId: string) {
    if (!token) return;
    setParsed(await getParsedResume(token, resumeId));
  }

  if (resumesState.loading) return <LoadingState label="Loading resumes..." />;

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-semibold">Resumes</h1>
      {error ?? resumesState.error ? <ErrorState message={error ?? resumesState.error ?? ""} /> : null}
      <Card>
        <label className="block text-sm font-medium">Upload PDF or DOCX</label>
        <Input className="mt-2" type="file" accept=".pdf,.docx" onChange={onUpload} />
      </Card>
      <DataTable
        columns={[
          { key: "name", header: "File", render: (resume) => resume.original_file_name },
          { key: "primary", header: "Primary", render: (resume) => resume.is_primary ? "Yes" : "No" },
          { key: "skills", header: "Skills", render: (resume) => resume.extracted_skills_json?.join(", ") || "None" },
          { key: "parsed", header: "Parsed", render: (resume) => <button className="underline" onClick={() => onParsed(resume.id)}>View parsed</button> },
        ]}
        emptyText="No resumes uploaded yet."
        rows={resumesState.data ?? []}
      />
      {parsed ? (
        <Card>
          <h2 className="text-lg font-semibold">Parsed Resume</h2>
          <p className="mt-2 text-sm">Skills: {parsed.skills.join(", ") || "None"}</p>
          <pre className="mt-3 overflow-auto rounded-md bg-slate-50 p-3 text-xs">{JSON.stringify(parsed, null, 2)}</pre>
        </Card>
      ) : null}
    </div>
  );
}

export function CandidateInterviewDetailView({ sessionId }: { sessionId: string }) {
  const { token } = useAuth();
  const sessionState = useApiState(() => getInterviewSession(token!, sessionId), [token, sessionId]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [message, setMessage] = useState<string | null>(null);

  async function submitAnswer(questionId: string) {
    if (!token) return;
    await answerQuestion(token, questionId, answers[questionId] ?? "");
    sessionState.setData(await getInterviewSession(token, sessionId));
    setMessage("Answer submitted and scored.");
  }

  async function onComplete() {
    if (!token) return;
    sessionState.setData(await completeInterview(token, sessionId));
    setMessage("Interview completed.");
  }

  if (sessionState.loading) return <LoadingState label="Loading interview..." />;
  if (sessionState.error) return <ErrorState message={sessionState.error} />;
  const session = sessionState.data;
  if (!session) return <EmptyState message="Interview not found." />;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Interview Session</h1>
          <p className="text-sm text-slate-600">Status: {session.status} · Overall: {session.overall_score ?? "N/A"}</p>
        </div>
        <Button disabled={session.status !== "in_progress"} onClick={onComplete}>Complete interview</Button>
      </div>
      {message ? <Alert>{message}</Alert> : null}
      {session.questions.map((question) => (
        <Card key={question.id}>
          <div className="flex items-center justify-between gap-3">
            <h2 className="font-semibold">{question.order_index}. {question.question_text}</h2>
            <Badge>{question.question_type}</Badge>
          </div>
          {question.answer ? (
            <Alert>Current score: {question.answer.score ?? "N/A"} · {String(question.answer.feedback_json?.summary ?? "Answer saved.")}</Alert>
          ) : null}
          <Textarea
            className="mt-3"
            disabled={session.status !== "in_progress"}
            onChange={(event) => setAnswers((current) => ({ ...current, [question.id]: event.target.value }))}
            placeholder="Type your answer"
            value={answers[question.id] ?? question.answer?.answer_text ?? ""}
          />
          <Button className="mt-3" disabled={session.status !== "in_progress"} onClick={() => submitAnswer(question.id)}>
            Submit answer
          </Button>
        </Card>
      ))}
    </div>
  );
}
