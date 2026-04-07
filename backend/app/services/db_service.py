import csv
import io
import logging
import os
import sqlite3
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
DB_PATH = os.path.join(DB_DIR, "wp200.db")


def _get_db() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = _get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            handle TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            email TEXT NOT NULL,
            kanji_name TEXT DEFAULT '',
            romaji_name TEXT DEFAULT '',
            registered_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            handle TEXT NOT NULL REFERENCES students(handle),
            created_at TEXT DEFAULT (datetime('now')),
            expires_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS otp_codes (
            handle TEXT PRIMARY KEY REFERENCES students(handle),
            otp TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            attempts INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            handle TEXT DEFAULT '',
            assignment_id INTEGER NOT NULL,
            code TEXT,
            files_json TEXT,
            deterministic_results_json TEXT,
            deterministic_score INTEGER DEFAULT 0,
            ai_score INTEGER DEFAULT 0,
            ai_max INTEGER DEFAULT 0,
            ai_feedback TEXT DEFAULT '',
            ai_raw_response TEXT DEFAULT '',
            total_proposed_score INTEGER DEFAULT 0,
            max_score INTEGER DEFAULT 100,
            status TEXT DEFAULT 'ai-graded',
            final_score INTEGER,
            final_feedback TEXT,
            published INTEGER DEFAULT 0,
            submitted_at TEXT DEFAULT (datetime('now')),
            reviewed_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_submissions_student ON submissions(student_id);
        CREATE INDEX IF NOT EXISTS idx_submissions_assignment ON submissions(assignment_id);
        CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
    """)
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


# Initialize on import
init_db()


# ========== Student Registry ==========

def upsert_student(handle: str, student_id: str, email: str,
                   kanji_name: str = "", romaji_name: str = ""):
    conn = _get_db()
    conn.execute("""
        INSERT INTO students (handle, student_id, email, kanji_name, romaji_name)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(handle) DO UPDATE SET
            student_id=excluded.student_id,
            email=excluded.email,
            kanji_name=excluded.kanji_name,
            romaji_name=excluded.romaji_name
    """, (handle, student_id, email, kanji_name, romaji_name))
    conn.commit()
    conn.close()


def get_student(handle: str) -> dict:
    conn = _get_db()
    row = conn.execute("SELECT * FROM students WHERE handle = ?", (handle,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_students() -> list:
    conn = _get_db()
    rows = conn.execute("SELECT * FROM students ORDER BY student_id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def is_registered(handle: str) -> bool:
    return get_student(handle) is not None


# ========== OTP ==========

def save_otp(handle: str, otp: str):
    conn = _get_db()
    conn.execute("""
        INSERT INTO otp_codes (handle, otp, created_at, attempts)
        VALUES (?, ?, datetime('now'), 0)
        ON CONFLICT(handle) DO UPDATE SET
            otp=excluded.otp, created_at=datetime('now'), attempts=0
    """, (handle, otp))
    conn.commit()
    conn.close()


def get_otp(handle: str) -> dict:
    conn = _get_db()
    row = conn.execute("SELECT * FROM otp_codes WHERE handle = ?", (handle,)).fetchone()
    conn.close()
    return dict(row) if row else None


def increment_otp_attempts(handle: str):
    conn = _get_db()
    conn.execute("UPDATE otp_codes SET attempts = attempts + 1 WHERE handle = ?", (handle,))
    conn.commit()
    conn.close()


def delete_otp(handle: str):
    conn = _get_db()
    conn.execute("DELETE FROM otp_codes WHERE handle = ?", (handle,))
    conn.commit()
    conn.close()


# ========== Sessions ==========

def save_session(token: str, handle: str, expires_at: str):
    conn = _get_db()
    conn.execute("""
        INSERT INTO sessions (token, handle, expires_at)
        VALUES (?, ?, ?)
    """, (token, handle, expires_at))
    conn.commit()
    conn.close()


def get_session(token: str) -> dict:
    conn = _get_db()
    row = conn.execute("""
        SELECT s.token, s.handle, s.created_at, s.expires_at,
               st.student_id, st.romaji_name, st.kanji_name
        FROM sessions s
        JOIN students st ON s.handle = st.handle
        WHERE s.token = ?
    """, (token,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_session(token: str):
    conn = _get_db()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def cleanup_expired_sessions():
    conn = _get_db()
    conn.execute("DELETE FROM sessions WHERE expires_at < datetime('now')")
    conn.commit()
    conn.close()


# ========== Submissions ==========

def _serialize_json(data) -> str:
    import json
    return json.dumps(data, default=str) if data else ""


def _deserialize_json(text: str):
    import json
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


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
    conn = _get_db()
    cursor = conn.execute("""
        INSERT INTO submissions (
            student_id, handle, assignment_id, code, files_json,
            deterministic_results_json, deterministic_score,
            ai_score, ai_max, ai_feedback, ai_raw_response,
            total_proposed_score, max_score, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ai-graded')
    """, (
        student_id, handle, assignment_id, code,
        _serialize_json(files),
        _serialize_json(deterministic_results),
        deterministic_score, ai_score, ai_max,
        ai_feedback, ai_raw_response, total, max_score,
    ))
    submission_id = cursor.lastrowid
    conn.commit()

    row = conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()
    conn.close()
    return _row_to_submission(row)


def get_submission(submission_id: int) -> dict:
    conn = _get_db()
    row = conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()
    conn.close()
    return _row_to_submission(row) if row else None


def get_submissions_by_student(student_id: str) -> list:
    conn = _get_db()
    rows = conn.execute(
        "SELECT * FROM submissions WHERE student_id = ? ORDER BY submitted_at DESC",
        (student_id,)
    ).fetchall()
    conn.close()
    return [_row_to_submission(r) for r in rows]


def get_published_grades(student_id: str) -> list:
    conn = _get_db()
    rows = conn.execute("""
        SELECT assignment_id, final_score, max_score, final_feedback
        FROM submissions
        WHERE student_id = ? AND published = 1
        ORDER BY assignment_id
    """, (student_id,)).fetchall()
    conn.close()
    return [
        {
            "assignment_id": r["assignment_id"],
            "score": r["final_score"],
            "max_score": r["max_score"],
            "feedback": r["final_feedback"],
        }
        for r in rows
    ]


def get_all_submissions(assignment_id: int = None, status: str = None) -> list:
    conn = _get_db()
    query = "SELECT * FROM submissions WHERE 1=1"
    params = []
    if assignment_id is not None:
        query += " AND assignment_id = ?"
        params.append(assignment_id)
    if status is not None:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY submitted_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_submission(r) for r in rows]


def update_submission(submission_id: int, updates: dict) -> dict:
    conn = _get_db()
    set_clauses = []
    params = []
    for key, val in updates.items():
        set_clauses.append(f"{key} = ?")
        params.append(val)
    params.append(submission_id)

    conn.execute(
        f"UPDATE submissions SET {', '.join(set_clauses)} WHERE id = ?",
        params,
    )
    conn.commit()
    row = conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()
    conn.close()
    return _row_to_submission(row) if row else None


def review_submission(submission_id: int, final_score: int, final_feedback: str, publish: bool = False) -> dict:
    return update_submission(submission_id, {
        "final_score": final_score,
        "final_feedback": final_feedback,
        "status": "published" if publish else "reviewed",
        "published": 1 if publish else 0,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
    })


def publish_submission(submission_id: int) -> dict:
    return update_submission(submission_id, {
        "status": "published",
        "published": 1,
    })


def _row_to_submission(row) -> dict:
    if not row:
        return None
    d = dict(row)
    d["files"] = _deserialize_json(d.pop("files_json", ""))
    d["deterministic_results"] = _deserialize_json(d.pop("deterministic_results_json", ""))
    d["published"] = bool(d.get("published", 0))
    return d


# ========== CSV Export ==========

def export_grades_csv(assignment_id: int = None) -> str:
    """Export all final grades as CSV. Returns CSV string.
    Columns: Student ID, Handle, Kanji Name, Romaji Name, Assignment, Score, Max Score, Feedback, Submitted, Reviewed
    """
    conn = _get_db()
    query = """
        SELECT sub.student_id, sub.handle,
               COALESCE(st.kanji_name, '') as kanji_name,
               COALESCE(st.romaji_name, '') as romaji_name,
               sub.assignment_id, sub.final_score, sub.max_score,
               sub.final_feedback, sub.submitted_at, sub.reviewed_at
        FROM submissions sub
        LEFT JOIN students st ON sub.student_id = st.student_id
        WHERE sub.published = 1
    """
    params = []
    if assignment_id is not None:
        query += " AND sub.assignment_id = ?"
        params.append(assignment_id)
    query += " ORDER BY sub.student_id, sub.assignment_id"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Student ID", "Handle", "Kanji Name", "Romaji Name",
        "Assignment", "Score", "Max Score", "Feedback",
        "Submitted", "Reviewed"
    ])
    for r in rows:
        writer.writerow([
            r["student_id"], r["handle"], r["kanji_name"], r["romaji_name"],
            r["assignment_id"], r["final_score"], r["max_score"],
            r["final_feedback"], r["submitted_at"], r["reviewed_at"],
        ])

    return output.getvalue()


def export_summary_csv() -> str:
    """Export grade summary: one row per student with all assignment scores.
    Designed for importing into university course management system.
    Columns: Student ID, Handle, Kanji Name, Romaji Name, A1, A2, ..., A9, Total, Average
    """
    conn = _get_db()
    students = conn.execute("""
        SELECT DISTINCT sub.student_id, sub.handle,
               COALESCE(st.kanji_name, '') as kanji_name,
               COALESCE(st.romaji_name, '') as romaji_name
        FROM submissions sub
        LEFT JOIN students st ON sub.student_id = st.student_id
        WHERE sub.published = 1
        ORDER BY sub.student_id
    """).fetchall()

    # Get all published scores per student
    all_scores = {}
    rows = conn.execute("""
        SELECT student_id, assignment_id, final_score, max_score
        FROM submissions
        WHERE published = 1
        ORDER BY student_id, assignment_id
    """).fetchall()
    conn.close()

    for r in rows:
        sid = r["student_id"]
        if sid not in all_scores:
            all_scores[sid] = {}
        all_scores[sid][r["assignment_id"]] = r["final_score"]

    output = io.StringIO()
    writer = csv.writer(output)
    header = ["Student ID", "Handle", "Kanji Name", "Romaji Name"]
    for i in range(1, 10):
        header.append(f"A{i}")
    header.extend(["Total", "Average"])
    writer.writerow(header)

    for s in students:
        sid = s["student_id"]
        scores = all_scores.get(sid, {})
        row = [sid, s["handle"], s["kanji_name"], s["romaji_name"]]
        total = 0
        count = 0
        for i in range(1, 10):
            score = scores.get(i, "")
            row.append(score)
            if score != "":
                total += score
                count += 1
        row.append(total)
        row.append(round(total / count, 1) if count > 0 else "")
        writer.writerow(row)

    return output.getvalue()
