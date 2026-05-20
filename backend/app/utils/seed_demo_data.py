from pathlib import Path

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.core.time import utc_now
from app.models.activity_log import ActivityLog
from app.models.application import Application
from app.models.candidate import CandidateProfile
from app.models.interview import CandidateAnswer, InterviewQuestion, InterviewSession
from app.models.job import Job
from app.models.recruiter import RecruiterProfile
from app.models.resume import Resume
from app.models.scoring import MatchScore
from app.models.user import Role, User
from app.utils.seed_roles import seed_default_roles


PASSWORD = "Password123!"


def seed_demo_data(db: Session) -> dict[str, str]:
    seed_default_roles(db)

    admin = _get_or_create_user(db, "admin@hireai.local", "Admin User", "admin")
    recruiter = _get_or_create_user(db, "recruiter@hireai.local", "Recruiter User", "recruiter")
    candidate = _get_or_create_user(db, "candidate@hireai.local", "Candidate User", "candidate")

    recruiter_profile = _get_or_create_recruiter_profile(db, recruiter)
    candidate_profile = _get_or_create_candidate_profile(db, candidate)

    jobs = [
        _get_or_create_job(
            db,
            recruiter_profile,
            title="Backend Engineer",
            description="Build production FastAPI services for a local-first hiring platform.",
            skills=["python", "fastapi", "postgresql", "docker"],
            seniority="mid",
            location="London",
            status="open",
        ),
        _get_or_create_job(
            db,
            recruiter_profile,
            title="Frontend Engineer",
            description="Create clean Next.js interfaces for hiring workflows.",
            skills=["typescript", "react", "next.js", "tailwind"],
            seniority="junior",
            location="Remote",
            status="open",
        ),
        _get_or_create_job(
            db,
            recruiter_profile,
            title="Data Analyst Intern",
            description="Analyze candidate pipeline data and reporting quality.",
            skills=["sql", "data analysis", "python"],
            seniority="internship",
            location="London",
            status="closed",
        ),
    ]

    applications = [
        _get_or_create_application(db, jobs[0], candidate_profile, "I have built FastAPI services with Docker."),
        _get_or_create_application(db, jobs[1], candidate_profile, "I enjoy building typed React interfaces."),
    ]

    resume = _get_or_create_resume(db, candidate_profile)
    score = _get_or_create_match_score(db, applications[0], candidate_profile, jobs[0])
    session = _get_or_create_interview(db, applications[0], candidate_profile, jobs[0])

    _log_once(db, admin.id, "demo_seeded", "user", admin.id, {"source": "seed_demo_data"})
    _log_once(db, recruiter.id, "job_created", "job", jobs[0].id, {"title": jobs[0].title})
    _log_once(db, candidate.id, "resume_uploaded", "resume", resume.id, {"file_type": resume.file_type})
    _log_once(db, candidate.id, "application_submitted", "application", applications[0].id, {"job": jobs[0].title})
    _log_once(db, candidate.id, "match_score_generated", "match_score", score.id, {"overall_score": score.overall_score})
    _log_once(db, candidate.id, "interview_completed", "interview_session", session.id, {"overall_score": session.overall_score})

    db.commit()
    return {
        "admin": admin.email,
        "recruiter": recruiter.email,
        "candidate": candidate.email,
    }


def _get_or_create_user(db: Session, email: str, full_name: str, role_name: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    role = db.query(Role).filter(Role.name == role_name).one()
    if not user:
        user = User(email=email, full_name=full_name, hashed_password=hash_password(PASSWORD), is_active=True)
        user.roles.append(role)
        db.add(user)
        db.flush()
        db.refresh(user)
    elif role not in user.roles:
        user.roles.append(role)
        db.flush()
    return user


def _get_or_create_recruiter_profile(db: Session, user: User) -> RecruiterProfile:
    profile = db.query(RecruiterProfile).filter(RecruiterProfile.user_id == user.id).first()
    if not profile:
        profile = RecruiterProfile(user_id=user.id)
        db.add(profile)
        db.flush()
    profile.company_name = "HireAI Labs"
    profile.company_website = "https://hireai.local"
    profile.company_size = "11-50"
    profile.industry = "Recruitment Technology"
    profile.position = "Talent Lead"
    profile.phone = "+44 7000 000000"
    profile.location = "London"
    profile.company_description = "Demo recruiting team using HireAI Local for structured hiring."
    profile.is_completed = True
    db.flush()
    db.refresh(profile)
    return profile


def _get_or_create_candidate_profile(db: Session, user: User) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=user.id)
        db.add(profile)
        db.flush()
    profile.headline = "Backend Engineer"
    profile.summary = "FastAPI and PostgreSQL candidate with Docker experience."
    profile.phone = "+44 7111 111111"
    profile.location = "London"
    profile.skills_json = ["python", "fastapi", "postgresql", "docker", "react"]
    profile.education_json = [{"degree": "BSc Computer Science", "institution": "Local University"}]
    profile.experience_json = [{"title": "Backend Developer", "years": 3}]
    profile.experience_years = 3
    profile.linkedin_url = "https://linkedin.com/in/hireai-demo-candidate"
    profile.github_url = "https://github.com/hireai-demo-candidate"
    profile.is_completed = True
    db.flush()
    db.refresh(profile)
    return profile


def _get_or_create_job(
    db: Session,
    recruiter: RecruiterProfile,
    *,
    title: str,
    description: str,
    skills: list[str],
    seniority: str,
    location: str,
    status: str,
) -> Job:
    job = db.query(Job).filter(Job.recruiter_id == recruiter.id, Job.title == title).first()
    if not job:
        job = Job(recruiter_id=recruiter.id, title=title, description=description)
        db.add(job)
        db.flush()
    job.description = description
    job.requirements_json = [f"Experience with {skill}" for skill in skills[:3]]
    job.skills_json = skills
    job.seniority = seniority
    job.location = location
    job.employment_type = "remote" if location.lower() == "remote" else "full_time"
    job.salary_min = 30000
    job.salary_max = 65000
    job.status = status
    db.flush()
    db.refresh(job)
    return job


def _get_or_create_application(db: Session, job: Job, candidate: CandidateProfile, cover_letter: str) -> Application:
    application = db.query(Application).filter(Application.job_id == job.id, Application.candidate_id == candidate.id).first()
    if not application:
        application = Application(job_id=job.id, candidate_id=candidate.id, cover_letter=cover_letter)
        db.add(application)
        db.flush()
    application.cover_letter = cover_letter
    application.status = "shortlisted" if job.title == "Backend Engineer" else "submitted"
    db.flush()
    db.refresh(application)
    return application


def _get_or_create_resume(db: Session, candidate: CandidateProfile) -> Resume:
    resume = db.query(Resume).filter(Resume.candidate_id == candidate.id, Resume.original_file_name == "demo_resume.pdf").first()
    storage_dir = Path("storage") / "resumes"
    storage_dir.mkdir(parents=True, exist_ok=True)
    file_path = storage_dir / "demo_resume.pdf"
    if not file_path.exists():
        file_path.write_bytes(b"%PDF-1.4\n% HireAI Local demo resume placeholder\n")
    if not resume:
        resume = Resume(
            candidate_id=candidate.id,
            file_name="demo_resume.pdf",
            original_file_name="demo_resume.pdf",
            file_path=str(file_path),
            file_type="pdf",
            file_size=file_path.stat().st_size,
            is_primary=True,
        )
        db.add(resume)
        db.flush()
    resume.extracted_text = "Python FastAPI PostgreSQL Docker React BSc Computer Science Backend Developer"
    resume.parsed_data_json = {
        "skills": ["python", "fastapi", "postgresql", "docker", "react"],
        "education": [{"degree": "BSc Computer Science"}],
        "experience": [{"title": "Backend Developer"}],
        "summary": "Backend engineer with API and database experience.",
        "parser_version": "rule_based_v1",
    }
    resume.extracted_skills_json = ["python", "fastapi", "postgresql", "docker", "react"]
    resume.is_primary = True
    resume.file_size = file_path.stat().st_size
    db.flush()
    db.refresh(resume)
    return resume


def _get_or_create_match_score(
    db: Session,
    application: Application,
    candidate: CandidateProfile,
    job: Job,
) -> MatchScore:
    score = db.query(MatchScore).filter(MatchScore.application_id == application.id).first()
    if not score:
        score = MatchScore(
            application_id=application.id,
            candidate_id=candidate.id,
            job_id=job.id,
            overall_score=92,
            skill_score=50,
            experience_score=17,
            education_score=10,
            location_score=15,
            explanation_json={},
            matched_skills_json=[],
            missing_skills_json=[],
            scoring_version="rule_based_v1",
        )
        db.add(score)
    score.overall_score = 92
    score.skill_score = 50
    score.experience_score = 17
    score.education_score = 10
    score.location_score = 15
    score.explanation_json = {
        "summary": "Strong demo match for the Backend Engineer role.",
        "skill_reason": "Matched all required backend skills.",
        "experience_reason": "Candidate is close to the expected mid-level experience.",
        "education_reason": "Education evidence found in parsed resume.",
        "location_reason": "Candidate location matches job location.",
        "recommendation": "strong_match",
    }
    score.matched_skills_json = ["python", "fastapi", "postgresql", "docker"]
    score.missing_skills_json = []
    db.flush()
    db.refresh(score)
    return score


def _get_or_create_interview(
    db: Session,
    application: Application,
    candidate: CandidateProfile,
    job: Job,
) -> InterviewSession:
    session = db.query(InterviewSession).filter(InterviewSession.application_id == application.id).first()
    if not session:
        session = InterviewSession(application_id=application.id, candidate_id=candidate.id, job_id=job.id)
        db.add(session)
        db.flush()
    session.status = "completed"
    session.overall_score = 86
    session.completed_at = session.completed_at or utc_now()
    session.feedback_json = {
        "summary": "Strong technical answers with practical project evidence.",
        "strengths": ["FastAPI", "Docker", "PostgreSQL"],
        "improvements": ["Add more detail about monitoring and deployment trade-offs."],
    }
    db.flush()

    questions = [
        ("How have you used FastAPI in a real project?", "technical", "fastapi", ["fastapi", "api", "sqlalchemy"]),
        ("Tell me about a difficult technical problem you solved.", "behavioral", None, ["problem", "solution"]),
    ]
    for index, (text, question_type, skill_tag, keywords) in enumerate(questions, start=1):
        question = (
            db.query(InterviewQuestion)
            .filter(InterviewQuestion.session_id == session.id, InterviewQuestion.order_index == index)
            .first()
        )
        if not question:
            question = InterviewQuestion(session_id=session.id, order_index=index, question_text=text, question_type=question_type)
            db.add(question)
            db.flush()
        question.question_text = text
        question.question_type = question_type
        question.skill_tag = skill_tag
        question.expected_signals_json = {"keywords": keywords, "good_answer_traits": ["specific", "practical"]}
        answer = db.query(CandidateAnswer).filter(CandidateAnswer.question_id == question.id).first()
        if not answer:
            answer = CandidateAnswer(question_id=question.id, answer_text="")
            db.add(answer)
            db.flush()
        answer.answer_text = "I used FastAPI with SQLAlchemy, PostgreSQL, Docker, testing, and clear API boundaries."
        answer.score = 8.6
        answer.feedback_json = {
            "summary": "Good practical answer.",
            "strengths": ["Mentions expected tools", "Shows project context"],
            "improvements": ["Add measurable impact."],
            "score_reason": "Strong keyword overlap and relevant implementation detail.",
        }
    db.flush()
    db.refresh(session)
    return session


def _log_once(db: Session, actor_user_id, action: str, entity_type: str, entity_id, metadata: dict | None = None) -> None:
    exists = (
        db.query(ActivityLog)
        .filter(
            ActivityLog.action == action,
            ActivityLog.entity_type == entity_type,
            ActivityLog.entity_id == entity_id,
        )
        .first()
    )
    if exists:
        return
    db.add(
        ActivityLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata,
        )
    )


def main() -> None:
    db = SessionLocal()
    try:
        accounts = seed_demo_data(db)
        print("Demo data seeded.")
        for role, email in accounts.items():
            print(f"{role}: {email} / {PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
