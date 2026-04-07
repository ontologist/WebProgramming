import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Simple JSON-file database for submissions and grades.
# Avoids requiring PostgreSQL for initial deployment.
# Can be replaced with SQLAlchemy + PostgreSQL later.

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
SUBMISSIONS_FILE = os.path.join(DB_DIR, "submissions.json")
COUNTER_FILE = os.path.join(DB_DIR, "counter.json")


def _ensure_db():
    os.makedirs(DB_DIR, exist_ok=True)
    if not os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, "w") as f:
            json.dump([], f)
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            json.dump({"next_id": 1}, f)


def _load_submissions() -> list:
    _ensure_db()
    with open(SUBMISSIONS_FILE, "r") as f:
        return json.load(f)


def _save_submissions(submissions: list):
    _ensure_db()
    with open(SUBMISSIONS_FILE, "w") as f:
        json.dump(submissions, f, indent=2, default=str)


def _next_id() -> int:
    _ensure_db()
    with open(COUNTER_FILE, "r") as f:
        data = json.load(f)
    sid = data["next_id"]
    data["next_id"] = sid + 1
    with open(COUNTER_FILE, "w") as f:
        json.dump(data, f)
    return sid


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
) -> dict:
    submissions = _load_submissions()
    submission_id = _next_id()

    submission = {
        "id": submission_id,
        "student_id": student_id,
        "assignment_id": assignment_id,
        "code": code,
        "files": files,
        "deterministic_results": deterministic_results,
        "deterministic_score": deterministic_score,
        "ai_score": ai_score,
        "ai_max": ai_max,
        "ai_feedback": ai_feedback,
        "ai_raw_response": ai_raw_response,
        "total_proposed_score": deterministic_score + ai_score,
        "max_score": max_score,
        "status": "ai-graded",  # submitted -> ai-graded -> reviewed -> published
        "final_score": None,
        "final_feedback": None,
        "published": False,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_at": None,
    }

    submissions.append(submission)
    _save_submissions(submissions)
    logger.info(f"Submission {submission_id} created for student {student_id}, assignment {assignment_id}")
    return submission


def get_submission(submission_id: int) -> dict:
    submissions = _load_submissions()
    for s in submissions:
        if s["id"] == submission_id:
            return s
    return None


def get_submissions_by_student(student_id: str) -> list:
    submissions = _load_submissions()
    return [s for s in submissions if s["student_id"] == student_id]


def get_published_grades(student_id: str) -> list:
    submissions = _load_submissions()
    grades = []
    for s in submissions:
        if s["student_id"] == student_id and s["published"]:
            grades.append({
                "assignment_id": s["assignment_id"],
                "score": s["final_score"],
                "max_score": s["max_score"],
                "feedback": s["final_feedback"],
            })
    return grades


def get_all_submissions(assignment_id: int = None, status: str = None) -> list:
    submissions = _load_submissions()
    results = submissions
    if assignment_id is not None:
        results = [s for s in results if s["assignment_id"] == assignment_id]
    if status is not None:
        results = [s for s in results if s["status"] == status]
    return results


def update_submission(submission_id: int, updates: dict) -> dict:
    submissions = _load_submissions()
    for i, s in enumerate(submissions):
        if s["id"] == submission_id:
            submissions[i].update(updates)
            _save_submissions(submissions)
            return submissions[i]
    return None


def review_submission(submission_id: int, final_score: int, final_feedback: str, publish: bool = False) -> dict:
    updates = {
        "final_score": final_score,
        "final_feedback": final_feedback,
        "status": "published" if publish else "reviewed",
        "published": publish,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
    }
    return update_submission(submission_id, updates)


def publish_submission(submission_id: int) -> dict:
    return update_submission(submission_id, {
        "status": "published",
        "published": True,
    })
