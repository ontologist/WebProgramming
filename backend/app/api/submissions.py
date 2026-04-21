# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import grading_service, db_service

router = APIRouter()


class SubmissionRequest(BaseModel):
    # student_id is accepted from the client but ignored: we derive the
    # authoritative value from the authenticated handle to prevent spoofing
    # and to survive a client that sends the wrong label (e.g. "INSTRUCTOR").
    student_id: Optional[str] = None
    handle: str = ""  # authenticated handle; required to satisfy the FK to students.handle
    assignment_id: int
    code: Optional[str] = None
    files: Optional[dict] = None  # {filename: content}
    language: str = "en"  # en, ja, zh, ko, es


class SubmissionResponse(BaseModel):
    submission_id: int
    status: str
    message: str


@router.post("/submit", response_model=SubmissionResponse)
async def submit_assignment(request: SubmissionRequest):
    if not request.code and not request.files:
        raise HTTPException(status_code=400, detail="No code or files provided")

    # Resolve submitter identity. Prefer the authenticated handle (required by
    # the FK to students.handle). Fall back to a student_id lookup for clients
    # that only send student_id. We then derive the authoritative student_id
    # from the student row — the client's label is never trusted.
    handle = (request.handle or "").strip().lower()
    student = db_service.get_student(handle) if handle else None
    if not student and request.student_id:
        student = next(
            (s for s in db_service.get_all_students() if s["student_id"] == request.student_id),
            None,
        )
    if not student:
        raise HTTPException(
            status_code=401,
            detail="Cannot identify submitter. Please log in again and resubmit.",
        )
    handle = student["handle"]
    authoritative_student_id = student["student_id"]

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
        student_id=authoritative_student_id,
        handle=handle,
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
