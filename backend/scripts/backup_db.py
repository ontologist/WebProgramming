# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
"""
Snapshot backup of the WP-200 SQLite database.

Uses SQLite's online backup API (sqlite3.Connection.backup), which is safe
to run while the backend is live — it reads pages under a shared lock and
cooperates with WAL mode.

Writes to:   backend/data/backups/wp200-YYYYMMDD-HHMMSS.db
Retention:   keeps the most recent RETAIN_COUNT snapshots; older ones are
             deleted.

Usage:
    cd backend
    ./venv/Scripts/python.exe scripts/backup_db.py
"""

from __future__ import annotations

import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

RETAIN_COUNT = 60  # ~2 months of daily backups

BACKEND = Path(__file__).resolve().parents[1]
SRC = BACKEND / "data" / "wp200.db"
BACKUP_DIR = BACKEND / "data" / "backups"


def prune(dir_: Path, keep: int) -> list[Path]:
    snapshots = sorted(dir_.glob("wp200-*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    stale = snapshots[keep:]
    for p in stale:
        try:
            p.unlink()
        except OSError as e:
            print(f"  warning: could not delete {p.name}: {e}", file=sys.stderr)
    return stale


def main() -> int:
    if not SRC.exists():
        print(f"source DB not found: {SRC}", file=sys.stderr)
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = BACKUP_DIR / f"wp200-{stamp}.db"

    # Online backup — no need to stop the backend.
    src_conn = sqlite3.connect(f"file:{SRC}?mode=ro", uri=True)
    dst_conn = sqlite3.connect(dst)
    try:
        with dst_conn:
            src_conn.backup(dst_conn)
    finally:
        dst_conn.close()
        src_conn.close()

    size_kb = dst.stat().st_size / 1024
    print(f"wrote {dst.relative_to(BACKEND)}  ({size_kb:.1f} KB)")

    pruned = prune(BACKUP_DIR, RETAIN_COUNT)
    if pruned:
        print(f"pruned {len(pruned)} old snapshot(s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
