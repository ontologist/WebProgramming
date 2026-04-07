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

@router.post("/students/upload-csv")
async def upload_student_csv(
    file: UploadFile = File(...),
    _auth: bool = Depends(verify_instructor),
):
    """Upload CSV file with student registry.
    Columns: Student ID, Handle, Kanji Last, Kanji First, Romaji Last, Romaji First
    """
    content = await file.read()
    text = content.decode("utf-8-sig")

    # Save to temp file and load
    import tempfile
    import os

    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
    tmp.write(text)
    tmp.close()

    try:
        count = auth_service.load_students_from_csv(tmp.name)
        return {"message": f"Loaded {count} students", "count": count}
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
                "email": s["email"],
                "kanji_name": s.get("kanji_name", ""),
                "romaji_name": s.get("romaji_name", ""),
            }
            for s in students.values()
        ],
    }
