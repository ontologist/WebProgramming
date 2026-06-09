# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
import csv
import logging
import random
import smtplib
import string
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings
from app.services import db_service

logger = logging.getLogger(__name__)

EMAIL_DOMAIN = "kwansei.ac.jp"
OTP_EXPIRY_MINUTES = 10
SESSION_EXPIRY_DAYS = 30


# ========== Student Registry ==========

def load_students_from_csv(csv_path: str) -> int:
    """Load students from CSV file.
    Expected columns: Student ID, Handle, Kanji Last, Kanji First, Romaji Last, Romaji First
    """
    count = 0
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header

        for row in reader:
            if len(row) < 6:
                continue

            student_id = row[0].strip()
            handle = row[1].strip().lower()
            kanji_last = row[2].strip()
            kanji_first = row[3].strip()
            romaji_last = row[4].strip()
            romaji_first = row[5].strip()

            if not student_id or not handle:
                continue

            db_service.upsert_student(
                handle=handle,
                student_id=student_id,
                email=f"{handle}@{EMAIL_DOMAIN}",
                kanji_name=f"{kanji_last} {kanji_first}",
                romaji_name=f"{romaji_last} {romaji_first}",
            )
            count += 1

    logger.info(f"Loaded {count} students from CSV")
    return count


def load_students_from_excel(file_path: str) -> int:
    """Load students from university enrollment Excel file (.xlsx).
    Parses the Kwansei Gakuin enrollment list format:
    - Row 4: Header row
    - Row 5+: Student data
    - Col C (idx 2): Student ID
    - Col D (idx 3): User ID (handle)
    - Col E (idx 4): Japanese name (kanji)
    - Col G (idx 6): Romaji name
    """
    import openpyxl

    # NOTE: read_only=True fails on KGU enrollment exports because the xlsx
    # has no <dimension> tag, which makes read-only mode stop at row 1.
    wb = openpyxl.load_workbook(file_path, read_only=False, data_only=True)
    ws = wb.active
    count = 0

    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i < 4:
            continue

        if not row or len(row) < 7:
            continue

        student_id = str(row[2] or "").strip()
        handle = str(row[3] or "").strip().lower()
        kanji_name = str(row[4] or "").strip().replace("\u3000", " ")
        romaji_name = str(row[6] or "").strip()

        if not student_id or not handle:
            continue

        db_service.upsert_student(
            handle=handle,
            student_id=student_id,
            email=f"{handle}@{EMAIL_DOMAIN}",
            kanji_name=kanji_name,
            romaji_name=romaji_name,
        )
        count += 1

    wb.close()
    logger.info(f"Loaded {count} students from Excel enrollment list")
    return count


def get_student(handle: str) -> dict:
    return db_service.get_student(handle.strip().lower())


def get_all_students() -> list:
    return db_service.get_all_students()


def is_registered(handle: str) -> bool:
    return db_service.is_registered(handle.strip().lower())


# ========== OTP Management ==========

def create_otp(handle: str) -> str:
    otp = "".join(random.choices(string.digits, k=6))
    db_service.save_otp(handle, otp)
    return otp


def verify_otp(handle: str, otp: str) -> bool:
    entry = db_service.get_otp(handle)
    if not entry:
        return False

    # Check expiry
    created = datetime.fromisoformat(entry["created_at"])
    # SQLite stores as naive UTC, so compare accordingly
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if isinstance(created, datetime) and created.tzinfo:
        created = created.replace(tzinfo=None)
    if (now - created) > timedelta(minutes=OTP_EXPIRY_MINUTES):
        db_service.delete_otp(handle)
        return False

    # Max attempts
    if entry["attempts"] >= 5:
        db_service.delete_otp(handle)
        return False

    db_service.increment_otp_attempts(handle)

    if entry["otp"] == otp.strip():
        db_service.delete_otp(handle)
        return True

    return False


# ========== Email Sending ==========

def _build_otp_email_html(name: str, otp: str) -> str:
    return f"""
    <html>
    <body style="font-family: 'Segoe UI', sans-serif; max-width: 500px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #2563eb, #7c3aed); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">💻 WP-200</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0;">Web Programming</p>
        </div>
        <div style="background: white; padding: 30px; border: 1px solid #e5e7eb; border-radius: 0 0 10px 10px;">
            <p>Hello {name},</p>
            <p>Your verification code for the WP-200 course site is:</p>
            <div style="text-align: center; margin: 25px 0;">
                <span style="font-size: 2.5rem; font-weight: bold; letter-spacing: 8px; color: #2563eb; background: #f0f4ff; padding: 15px 30px; border-radius: 10px; border: 2px solid #2563eb;">{otp}</span>
            </div>
            <p>This code expires in {OTP_EXPIRY_MINUTES} minutes.</p>
            <p style="color: #6b7280; font-size: 0.9rem;">If you did not request this code, please ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
            <p style="color: #9ca3af; font-size: 0.8rem; text-align: center;">Kwansei Gakuin University - School of Policy Studies</p>
        </div>
    </body>
    </html>
    """


async def send_otp_email(handle: str, otp: str) -> bool:
    email = f"{handle}@{EMAIL_DOMAIN}"
    student = get_student(handle)
    name = student.get("romaji_name", handle) if student else handle

    subject = "WP-200 Web Programming - Login Verification Code"
    body_html = _build_otp_email_html(name, otp)
    body_text = f"Your WP-200 verification code is: {otp}\nExpires in {OTP_EXPIRY_MINUTES} minutes."

    if settings.CLOUDFLARE_EMAIL_WORKER_URL:
        return await _send_via_cloudflare(email, subject, body_html, body_text)

    return _send_via_smtp(email, subject, body_html, body_text)


async def _send_via_cloudflare(email: str, subject: str, body_html: str, body_text: str) -> bool:
    import httpx
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.CLOUDFLARE_EMAIL_WORKER_URL,
                json={"to": email, "subject": subject, "html": body_html, "text": body_text},
                headers={
                    "Authorization": f"Bearer {settings.CLOUDFLARE_EMAIL_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            if response.status_code == 200:
                logger.info(f"OTP email sent via Cloudflare to {email}")
                return True
            logger.error(f"Cloudflare email failed: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"Cloudflare email error: {e}")
        return False


def _send_via_smtp(email: str, subject: str, body_html: str, body_text: str) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USERNAME
    msg["To"] = email
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"OTP email sent via SMTP to {email}")
        return True
    except Exception as e:
        logger.error(f"SMTP email error: {e}")
        return False


# ========== Session Management ==========

def create_session(handle: str) -> str:
    token = "".join(random.choices(string.ascii_letters + string.digits, k=48))
    expires_at = (datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS)).isoformat()
    db_service.save_session(token, handle, expires_at)
    return token


def validate_session(token: str) -> dict:
    if not token:
        return None

    session = db_service.get_session(token)
    if not session:
        return None

    # Check expiry
    expires = datetime.fromisoformat(session["expires_at"])
    now = datetime.now(timezone.utc)
    if expires.tzinfo is None:
        now = now.replace(tzinfo=None)
    if now > expires:
        db_service.delete_session(token)
        return None

    return {
        "handle": session["handle"],
        "student_id": session["student_id"],
        "name": session.get("romaji_name", session["handle"]),
        "kanji_name": session.get("kanji_name", ""),
    }


def invalidate_session(token: str):
    db_service.delete_session(token)
