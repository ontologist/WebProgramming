import csv
import io
import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select, update, delete

from app.core.database import SessionLocal, engine, get_engine_type
from app.core.models import Base, Student, Session, OTPCode, Submission

logger = logging.getLogger(__name__)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized ({get_engine_type()})")


# Initialize on import
init_db()


def _utcnow():
    return datetime.now(timezone.utc)


def _json_dumps(data) -> str:
    return json.dumps(data, default=str) if data else ""


def _json_loads(text: str):
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


# ========== Students ==========

def upsert_student(handle: str, student_id: str, email: str,
                   kanji_name: str = "", romaji_name: str = ""):
    with SessionLocal() as db:
        existing = db.get(Student, handle)
        if existing:
            existing.student_id = student_id
            existing.email = email
            existing.kanji_name = kanji_name
            existing.romaji_name = romaji_name
        else:
            db.add(Student(
                handle=handle, student_id=student_id, email=email,
                kanji_name=kanji_name, romaji_name=romaji_name,
            ))
        db.commit()


def get_student(handle: str) -> dict:
    with SessionLocal() as db:
        s = db.get(Student, handle)
        return _student_to_dict(s) if s else None


def get_all_students() -> list:
    with SessionLocal() as db:
        rows = db.execute(select(Student).order_by(Student.student_id)).scalars().all()
        return [_student_to_dict(s) for s in rows]


def is_registered(handle: str) -> bool:
    return get_student(handle) is not None


def _student_to_dict(s: Student) -> dict:
    return {
        "handle": s.handle,
        "student_id": s.student_id,
        "email": s.email,
        "kanji_name": s.kanji_name or "",
        "romaji_name": s.romaji_name or "",
    }


# ========== OTP ==========

def save_otp(handle: str, otp: str):
    with SessionLocal() as db:
        existing = db.get(OTPCode, handle)
        if existing:
            existing.otp = otp
            existing.created_at = _utcnow()
            existing.attempts = 0
        else:
            db.add(OTPCode(handle=handle, otp=otp, created_at=_utcnow(), attempts=0))
        db.commit()


def get_otp(handle: str) -> dict:
    with SessionLocal() as db:
        o = db.get(OTPCode, handle)
        if not o:
            return None
        return {
            "handle": o.handle,
            "otp": o.otp,
            "created_at": o.created_at.isoformat() if o.created_at else "",
            "attempts": o.attempts,
        }


def increment_otp_attempts(handle: str):
    with SessionLocal() as db:
        db.execute(update(OTPCode).where(OTPCode.handle == handle).values(attempts=OTPCode.attempts + 1))
        db.commit()


def delete_otp(handle: str):
    with SessionLocal() as db:
        db.execute(delete(OTPCode).where(OTPCode.handle == handle))
        db.commit()


# ========== Sessions ==========

def save_session(token: str, handle: str, expires_at: str):
    with SessionLocal() as db:
        db.add(Session(
            token=token, handle=handle,
            expires_at=datetime.fromisoformat(expires_at),
        ))
        db.commit()


def get_session(token: str) -> dict:
    with SessionLocal() as db:
        sess = db.get(Session, token)
        if not sess:
            return None
        student = db.get(Student, sess.handle)
        return {
            "token": sess.token,
            "handle": sess.handle,
            "created_at": sess.created_at.isoformat() if sess.created_at else "",
            "expires_at": sess.expires_at.isoformat() if sess.expires_at else "",
            "student_id": student.student_id if student else "",
            "romaji_name": student.romaji_name if student else "",
            "kanji_name": student.kanji_name if student else "",
        }


def delete_session(token: str):
    with SessionLocal() as db:
        db.execute(delete(Session).where(Session.token == token))
        db.commit()


def cleanup_expired_sessions():
    with SessionLocal() as db:
        db.execute(delete(Session).where(Session.expires_at < _utcnow()))
        db.commit()


# ========== Submissions ==========

def create_submission(
    student_id: str,
    assignment_id: int,
    code: str = None,
    files: dict = None,
    deterministic_results: list = None,
    deterministic_score: int = 0,
    ai_score: int = 0,
    ai_max: int = 0,
    ai_feedback: str = "",
    ai_raw_response: str = "",
    max_score: int = 100,
    handle: str = "",
) -> dict:
    total = deterministic_score + ai_score
    with SessionLocal() as db:
        sub = Submission(
            student_id=student_id, handle=handle, assignment_id=assignment_id,
            code=code, files_json=_json_dumps(files),
            deterministic_results_json=_json_dumps(deterministic_results),
            deterministic_score=deterministic_score,
            ai_score=ai_score, ai_max=ai_max,
            ai_feedback=ai_feedback, ai_raw_response=ai_raw_response,
            total_proposed_score=total, max_score=max_score,
            status="ai-graded",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return _submission_to_dict(sub)


def get_submission(submission_id: int) -> dict:
    with SessionLocal() as db:
        sub = db.get(Submission, submission_id)
        return _submission_to_dict(sub) if sub else None


def get_submissions_by_student(student_id: str) -> list:
    with SessionLocal() as db:
        rows = db.execute(
            select(Submission).where(Submission.student_id == student_id)
            .order_by(Submission.submitted_at.desc())
        ).scalars().all()
        return [_submission_to_dict(s) for s in rows]


def get_published_grades(student_id: str) -> list:
    with SessionLocal() as db:
        rows = db.execute(
            select(Submission)
            .where(Submission.student_id == student_id, Submission.published == True)
            .order_by(Submission.assignment_id)
        ).scalars().all()
        return [
            {
                "assignment_id": s.assignment_id,
                "score": s.final_score,
                "max_score": s.max_score,
                "feedback": s.final_feedback,
            }
            for s in rows
        ]


def get_all_submissions(assignment_id: int = None, status: str = None) -> list:
    with SessionLocal() as db:
        q = select(Submission)
        if assignment_id is not None:
            q = q.where(Submission.assignment_id == assignment_id)
        if status is not None:
            q = q.where(Submission.status == status)
        q = q.order_by(Submission.submitted_at.desc())
        rows = db.execute(q).scalars().all()
        return [_submission_to_dict(s) for s in rows]


def update_submission(submission_id: int, updates: dict) -> dict:
    with SessionLocal() as db:
        sub = db.get(Submission, submission_id)
        if not sub:
            return None
        for key, val in updates.items():
            setattr(sub, key, val)
        db.commit()
        db.refresh(sub)
        return _submission_to_dict(sub)


def review_submission(submission_id: int, final_score: int, final_feedback: str, publish: bool = False) -> dict:
    return update_submission(submission_id, {
        "final_score": final_score,
        "final_feedback": final_feedback,
        "status": "published" if publish else "reviewed",
        "published": publish,
        "reviewed_at": _utcnow(),
    })


def publish_submission(submission_id: int) -> dict:
    return update_submission(submission_id, {
        "status": "published",
        "published": True,
    })


def _submission_to_dict(s: Submission) -> dict:
    if not s:
        return None
    return {
        "id": s.id,
        "student_id": s.student_id,
        "handle": s.handle or "",
        "assignment_id": s.assignment_id,
        "code": s.code,
        "files": _json_loads(s.files_json),
        "deterministic_results": _json_loads(s.deterministic_results_json),
        "deterministic_score": s.deterministic_score,
        "ai_score": s.ai_score,
        "ai_max": s.ai_max,
        "ai_feedback": s.ai_feedback,
        "ai_raw_response": s.ai_raw_response,
        "total_proposed_score": s.total_proposed_score,
        "max_score": s.max_score,
        "status": s.status,
        "final_score": s.final_score,
        "final_feedback": s.final_feedback,
        "published": bool(s.published),
        "submitted_at": s.submitted_at.isoformat() if s.submitted_at else "",
        "reviewed_at": s.reviewed_at.isoformat() if s.reviewed_at else None,
    }


# ========== CSV Export ==========

def export_grades_csv(assignment_id: int = None) -> str:
    """Export all published grades as CSV."""
    with SessionLocal() as db:
        q = (
            select(
                Submission.student_id, Submission.handle, Submission.assignment_id,
                Submission.final_score, Submission.max_score, Submission.final_feedback,
                Submission.submitted_at, Submission.reviewed_at,
                Student.kanji_name, Student.romaji_name,
            )
            .outerjoin(Student, Submission.handle == Student.handle)
            .where(Submission.published == True)
        )
        if assignment_id is not None:
            q = q.where(Submission.assignment_id == assignment_id)
        q = q.order_by(Submission.student_id, Submission.assignment_id)
        rows = db.execute(q).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Student ID", "Handle", "Kanji Name", "Romaji Name",
        "Assignment", "Score", "Max Score", "Feedback",
        "Submitted", "Reviewed",
    ])
    for r in rows:
        writer.writerow([
            r.student_id, r.handle, r.kanji_name or "", r.romaji_name or "",
            r.assignment_id, r.final_score, r.max_score,
            r.final_feedback or "",
            r.submitted_at.isoformat() if r.submitted_at else "",
            r.reviewed_at.isoformat() if r.reviewed_at else "",
        ])
    return output.getvalue()


def export_summary_csv() -> str:
    """Export grade summary: one row per student, all assignment scores.
    Designed for university course management system import.
    """
    with SessionLocal() as db:
        # Get all students with published grades
        student_rows = db.execute(
            select(
                Submission.student_id, Submission.handle,
                Student.kanji_name, Student.romaji_name,
            )
            .outerjoin(Student, Submission.handle == Student.handle)
            .where(Submission.published == True)
            .group_by(Submission.student_id, Submission.handle,
                      Student.kanji_name, Student.romaji_name)
            .order_by(Submission.student_id)
        ).all()

        # Get all published scores
        score_rows = db.execute(
            select(Submission.student_id, Submission.assignment_id, Submission.final_score)
            .where(Submission.published == True)
        ).all()

    # Build scores lookup
    scores = {}
    for r in score_rows:
        scores.setdefault(r.student_id, {})[r.assignment_id] = r.final_score

    output = io.StringIO()
    writer = csv.writer(output)

    header = ["Student ID", "Handle", "Kanji Name", "Romaji Name"]
    for i in range(1, 10):
        header.append(f"A{i}")
    header.extend(["Total", "Average"])
    writer.writerow(header)

    for s in student_rows:
        sid = s.student_id
        student_scores = scores.get(sid, {})
        row = [sid, s.handle, s.kanji_name or "", s.romaji_name or ""]
        total = 0
        count = 0
        for i in range(1, 10):
            score = student_scores.get(i, "")
            row.append(score)
            if score != "":
                total += score
                count += 1
        row.append(total)
        row.append(round(total / count, 1) if count > 0 else "")
        writer.writerow(row)

    return output.getvalue()


def get_db_info() -> dict:
    """Return database type and stats."""
    engine_type = get_engine_type()
    with SessionLocal() as db:
        student_count = db.query(Student).count()
        submission_count = db.query(Submission).count()
        published_count = db.query(Submission).filter(Submission.published == True).count()
    return {
        "engine": engine_type,
        "students": student_count,
        "submissions": submission_count,
        "published_grades": published_count,
    }
