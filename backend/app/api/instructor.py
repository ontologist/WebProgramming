from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets

from app.services import db_service, grading_service
from app.core.config import settings

router = APIRouter()
security = HTTPBasic()


def verify_instructor(credentials: HTTPBasicCredentials = Depends(security)):
    correct_password = secrets.compare_digest(credentials.password, settings.INSTRUCTOR_PASSWORD)
    if credentials.username != "instructor" or not correct_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username


class ReviewRequest(BaseModel):
    final_score: int
    final_feedback: str
    publish: bool = False


# --- Instructor Dashboard API ---

@router.get("/submissions")
async def list_submissions(
    assignment_id: int = None,
    status: str = None,
    _user: str = Depends(verify_instructor),
):
    submissions = db_service.get_all_submissions(assignment_id=assignment_id, status=status)
    # Remove raw code from listing to keep response size manageable
    summary = []
    for s in submissions:
        summary.append({
            "id": s["id"],
            "student_id": s["student_id"],
            "assignment_id": s["assignment_id"],
            "assignment_name": grading_service.ASSIGNMENT_RUBRICS.get(s["assignment_id"], {}).get("name", "Unknown"),
            "deterministic_score": s["deterministic_score"],
            "ai_score": s["ai_score"],
            "total_proposed_score": s["total_proposed_score"],
            "max_score": s["max_score"],
            "final_score": s["final_score"],
            "status": s["status"],
            "published": s["published"],
            "submitted_at": s["submitted_at"],
            "reviewed_at": s["reviewed_at"],
        })
    return {"submissions": summary}


@router.get("/submissions/{submission_id}")
async def get_submission_detail(
    submission_id: int,
    _user: str = Depends(verify_instructor),
):
    submission = db_service.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.post("/submissions/{submission_id}/review")
async def review_submission(
    submission_id: int,
    review: ReviewRequest,
    _user: str = Depends(verify_instructor),
):
    submission = db_service.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    updated = db_service.review_submission(
        submission_id=submission_id,
        final_score=review.final_score,
        final_feedback=review.final_feedback,
        publish=review.publish,
    )
    return {"message": "Submission reviewed", "submission": updated}


@router.post("/submissions/{submission_id}/publish")
async def publish_submission(
    submission_id: int,
    _user: str = Depends(verify_instructor),
):
    submission = db_service.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission["final_score"] is None:
        raise HTTPException(status_code=400, detail="Please review and set a final score before publishing")

    updated = db_service.publish_submission(submission_id)
    return {"message": "Grade published", "submission": updated}


@router.get("/rubrics")
async def list_rubrics(_user: str = Depends(verify_instructor)):
    rubrics = {}
    for aid, rubric in grading_service.ASSIGNMENT_RUBRICS.items():
        rubrics[aid] = {
            "name": rubric["name"],
            "max_score": rubric["max_score"],
            "deterministic_checks": [c["name"] for c in rubric["deterministic_checks"]],
            "ai_criteria": rubric["ai_criteria"],
        }
    return {"rubrics": rubrics}
