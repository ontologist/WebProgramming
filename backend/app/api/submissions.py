from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import grading_service, db_service

router = APIRouter()


class SubmissionRequest(BaseModel):
    student_id: str
    assignment_id: int
    code: str = None
    files: dict = None  # {filename: content}
    language: str = "en"  # en, ja, zh, ko, es


class SubmissionResponse(BaseModel):
    submission_id: int
    status: str
    message: str


@router.post("/submit", response_model=SubmissionResponse)
async def submit_assignment(request: SubmissionRequest):
    if not request.code and not request.files:
        raise HTTPException(status_code=400, detail="No code or files provided")

    rubric = grading_service.get_rubric(request.assignment_id)
    if not rubric:
        raise HTTPException(status_code=400, detail=f"Unknown assignment: {request.assignment_id}")

    # Run deterministic checks
    det_results = grading_service.run_deterministic_checks(
        request.assignment_id, request.code, request.files
    )
    det_score = sum(r["points"] for r in det_results)

    # Run AI evaluation
    ai_result = await grading_service.ai_evaluate(
        request.assignment_id, request.code, request.files, det_results, request.language
    )

    # Save submission
    submission = db_service.create_submission(
        student_id=request.student_id,
        assignment_id=request.assignment_id,
        code=request.code,
        files=request.files,
        deterministic_results=det_results,
        deterministic_score=det_score,
        ai_score=ai_result["ai_score"],
        ai_max=ai_result["ai_max"],
        ai_feedback=ai_result["ai_feedback"],
        ai_raw_response=ai_result.get("ai_raw_response", ""),
        max_score=rubric["max_score"],
    )

    return SubmissionResponse(
        submission_id=submission["id"],
        status="submitted",
        message="Your assignment has been submitted and is being evaluated. Your instructor will review and publish your grade.",
    )


@router.get("/grades/{student_id}")
async def get_grades(student_id: str):
    grades = db_service.get_published_grades(student_id)
    return {"student_id": student_id, "grades": grades}
