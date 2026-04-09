# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
import io

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets

from app.services import auth_service
from app.core.config import settings

router = APIRouter()
security = HTTPBasic()


def verify_instructor(credentials: HTTPBasicCredentials = Depends(security)):
    if not secrets.compare_digest(credentials.password, settings.INSTRUCTOR_PASSWORD):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return True


# ========== Student Auth Endpoints ==========

class RequestOTPBody(BaseModel):
    handle: str


class VerifyOTPBody(BaseModel):
    handle: str
    otp: str


class ValidateSessionBody(BaseModel):
    token: str


@router.post("/request-otp")
async def request_otp(body: RequestOTPBody):
    handle = body.handle.strip().lower()

    if not auth_service.is_registered(handle):
        raise HTTPException(
            status_code=404,
            detail="Handle not found. Please ensure you are registered for this course."
        )

    otp = auth_service.create_otp(handle)
    email_sent = await auth_service.send_otp_email(handle, otp)

    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send verification email. Please contact your instructor."
        )

    student = auth_service.get_student(handle)
    email = student["email"]
    # Mask email: show first 3 chars + domain
    masked = email[:3] + "***@" + email.split("@")[1]

    return {
        "message": "Verification code sent",
        "email_masked": masked,
    }


@router.post("/verify-otp")
async def verify_otp(body: VerifyOTPBody):
    handle = body.handle.strip().lower()

    if not auth_service.is_registered(handle):
        raise HTTPException(status_code=404, detail="Handle not found")

    if auth_service.verify_otp(handle, body.otp):
        token = auth_service.create_session(handle)
        student = auth_service.get_student(handle)

        return {
            "authenticated": True,
            "token": token,
            "student": {
                "handle": handle,
                "student_id": student["student_id"],
                "name": student.get("romaji_name", handle),
                "kanji_name": student.get("kanji_name", ""),
            },
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid or expired verification code")


@router.post("/validate-session")
async def validate_session(body: ValidateSessionBody):
    session = auth_service.validate_session(body.token)
    if session:
        return {
            "valid": True,
            "handle": session["handle"],
            "student_id": session["student_id"],
            "name": session["name"],
        }
    return {"valid": False}


@router.post("/logout")
async def logout(body: ValidateSessionBody):
    auth_service.invalidate_session(body.token)
    return {"message": "Logged out"}


# ========== Instructor: Student Management ==========

@router.post("/students/upload")
async def upload_student_list(
    file: UploadFile = File(...),
    _auth: bool = Depends(verify_instructor),
):
    """Upload student registry file (.xlsx or .csv).
    - Excel (.xlsx): Kwansei Gakuin enrollment list format (auto-detected columns)
    - CSV: Student ID, Handle, Kanji Last, Kanji First, Romaji Last, Romaji First
    """
    import tempfile
    import os

    content = await file.read()
    filename = file.filename or ""
    is_excel = filename.lower().endswith((".xlsx", ".xls"))

    suffix = ".xlsx" if is_excel else ".csv"
    mode = "wb" if is_excel else "w"

    tmp = tempfile.NamedTemporaryFile(mode=mode, suffix=suffix, delete=False,
                                      **({"encoding": "utf-8"} if not is_excel else {}))
    if is_excel:
        tmp.write(content)
    else:
        tmp.write(content.decode("utf-8-sig"))
    tmp.close()

    try:
        if is_excel:
            count = auth_service.load_students_from_excel(tmp.name)
        else:
            count = auth_service.load_students_from_csv(tmp.name)
        return {"message": f"Loaded {count} students from {filename}", "count": count}
    finally:
        os.unlink(tmp.name)


@router.get("/students/list")
async def list_students(_auth: bool = Depends(verify_instructor)):
    students = auth_service.get_all_students()
    return {
        "count": len(students),
        "students": [
            {
                "student_id": s["student_id"],
                "handle": s["handle"],
                "email": s.get("email", ""),
                "kanji_name": s.get("kanji_name", ""),
                "romaji_name": s.get("romaji_name", ""),
            }
            for s in students
        ],
    }
