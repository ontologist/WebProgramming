import csv
import json
import logging
import os
import random
import smtplib
import string
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
OTP_FILE = os.path.join(DATA_DIR, "otp_store.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")

EMAIL_DOMAIN = "kwansei.ac.jp"
OTP_EXPIRY_MINUTES = 10
SESSION_EXPIRY_DAYS = 30


def _ensure_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    for filepath in [STUDENTS_FILE, OTP_FILE, SESSIONS_FILE]:
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                json.dump({} if filepath != SESSIONS_FILE else {}, f)


def _load_json(filepath: str) -> dict:
    _ensure_data()
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(filepath: str, data: dict):
    _ensure_data()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


# ========== Student Registry ==========

def load_students_from_csv(csv_path: str) -> int:
    """Load students from CSV file.
    Expected columns: Student ID, Handle, Kanji Last, Kanji First, Romaji Last, Romaji First
    """
    students = {}
    count = 0

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # skip header row

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

            students[handle] = {
                "student_id": student_id,
                "handle": handle,
                "email": f"{handle}@{EMAIL_DOMAIN}",
                "kanji_name": f"{kanji_last} {kanji_first}",
                "romaji_name": f"{romaji_last} {romaji_first}",
            }
            count += 1

    _save_json(STUDENTS_FILE, students)
    logger.info(f"Loaded {count} students from CSV")
    return count


def load_students_from_data(rows: list) -> int:
    """Load students from list of dicts (API upload)."""
    students = _load_json(STUDENTS_FILE)
    count = 0

    for row in rows:
        handle = row.get("handle", "").strip().lower()
        student_id = row.get("student_id", "").strip()
        if not handle or not student_id:
            continue

        students[handle] = {
            "student_id": student_id,
            "handle": handle,
            "email": f"{handle}@{EMAIL_DOMAIN}",
            "kanji_name": f"{row.get('kanji_last', '')} {row.get('kanji_first', '')}".strip(),
            "romaji_name": f"{row.get('romaji_last', '')} {row.get('romaji_first', '')}".strip(),
        }
        count += 1

    _save_json(STUDENTS_FILE, students)
    logger.info(f"Loaded {count} students via API")
    return count


def get_student(handle: str) -> dict:
    handle = handle.strip().lower()
    students = _load_json(STUDENTS_FILE)
    return students.get(handle)


def get_all_students() -> dict:
    return _load_json(STUDENTS_FILE)


def is_registered(handle: str) -> bool:
    return get_student(handle) is not None


# ========== OTP Management ==========

def _generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def create_otp(handle: str) -> str:
    """Generate and store a 6-digit OTP for the given handle."""
    otp_store = _load_json(OTP_FILE)
    otp = _generate_otp()
    otp_store[handle] = {
        "otp": otp,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "attempts": 0,
    }
    _save_json(OTP_FILE, otp_store)
    return otp


def verify_otp(handle: str, otp: str) -> bool:
    """Verify OTP for the given handle. Returns True if valid."""
    otp_store = _load_json(OTP_FILE)
    entry = otp_store.get(handle)

    if not entry:
        return False

    # Check expiry
    created = datetime.fromisoformat(entry["created_at"])
    if datetime.now(timezone.utc) - created > timedelta(minutes=OTP_EXPIRY_MINUTES):
        del otp_store[handle]
        _save_json(OTP_FILE, otp_store)
        return False

    # Check max attempts
    if entry["attempts"] >= 5:
        del otp_store[handle]
        _save_json(OTP_FILE, otp_store)
        return False

    # Increment attempts
    entry["attempts"] += 1
    _save_json(OTP_FILE, otp_store)

    if entry["otp"] == otp.strip():
        # Valid - clean up
        del otp_store[handle]
        _save_json(OTP_FILE, otp_store)
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
    """Send OTP email. Uses Cloudflare Email Workers if configured, otherwise SMTP."""
    email = f"{handle}@{EMAIL_DOMAIN}"
    student = get_student(handle)
    name = student.get("romaji_name", handle) if student else handle

    subject = "WP-200 Web Programming - Login Verification Code"
    body_html = _build_otp_email_html(name, otp)
    body_text = f"Your WP-200 verification code is: {otp}\nExpires in {OTP_EXPIRY_MINUTES} minutes."

    # Try Cloudflare Email Workers first
    if settings.CLOUDFLARE_EMAIL_WORKER_URL:
        return await _send_via_cloudflare(email, subject, body_html, body_text)

    # Fallback to SMTP
    return _send_via_smtp(email, subject, body_html, body_text)


async def _send_via_cloudflare(email: str, subject: str, body_html: str, body_text: str) -> bool:
    """Send email via Cloudflare Email Worker."""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.CLOUDFLARE_EMAIL_WORKER_URL,
                json={
                    "to": email,
                    "subject": subject,
                    "html": body_html,
                    "text": body_text,
                },
                headers={
                    "Authorization": f"Bearer {settings.CLOUDFLARE_EMAIL_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            if response.status_code == 200:
                logger.info(f"OTP email sent via Cloudflare to {email}")
                return True
            else:
                logger.error(f"Cloudflare email failed: {response.status_code} {response.text}")
                return False
    except Exception as e:
        logger.error(f"Cloudflare email error: {e}")
        return False


def _send_via_smtp(email: str, subject: str, body_html: str, body_text: str) -> bool:
    """Send email via SMTP (fallback)."""
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
    """Create a session token for authenticated user."""
    sessions = _load_json(SESSIONS_FILE)
    token = "".join(random.choices(string.ascii_letters + string.digits, k=48))

    student = get_student(handle)
    sessions[token] = {
        "handle": handle,
        "student_id": student["student_id"] if student else "",
        "name": student.get("romaji_name", handle) if student else handle,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS)).isoformat(),
    }
    _save_json(SESSIONS_FILE, sessions)
    return token


def validate_session(token: str) -> dict:
    """Validate session token. Returns session data or None."""
    if not token:
        return None

    sessions = _load_json(SESSIONS_FILE)
    session = sessions.get(token)

    if not session:
        return None

    # Check expiry
    expires = datetime.fromisoformat(session["expires_at"])
    if datetime.now(timezone.utc) > expires:
        del sessions[token]
        _save_json(SESSIONS_FILE, sessions)
        return None

    return session


def invalidate_session(token: str):
    """Remove a session token."""
    sessions = _load_json(SESSIONS_FILE)
    if token in sessions:
        del sessions[token]
        _save_json(SESSIONS_FILE, sessions)
