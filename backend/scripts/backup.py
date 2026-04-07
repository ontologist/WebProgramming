# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
"""
Automated backup script for WP-200 course database.

Backs up:
  1. PostgreSQL database (pg_dump) if available
  2. SQLite database file (copy) if present
  3. Knowledge base files
  4. Student submissions data

Backups are saved to a configurable folder with timestamped names.
Set up Windows Task Scheduler to run this daily.

Usage:
    python scripts/backup.py
    python scripts/backup.py --backup-dir "D:/OneDrive/WP200-Backups"
    python scripts/backup.py --backup-dir "C:/Users/YourName/Google Drive/WP200-Backups"

Windows Task Scheduler setup:
    1. Open Task Scheduler (taskschd.msc)
    2. Create Basic Task -> "WP200 Daily Backup"
    3. Trigger: Daily, at your preferred time (e.g., 2:00 AM)
    4. Action: Start a program
       Program: C:/path/to/venv/Scripts/python.exe
       Arguments: scripts/backup.py --backup-dir "D:/OneDrive/WP200-Backups"
       Start in: C:/path/to/WebProgramming/backend
    5. Finish
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DEFAULT_BACKUP_DIR = os.path.join(os.path.dirname(__file__), "..", "backups")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")
SQLITE_PATH = os.path.join(DATA_DIR, "wp200.db")

# Max backups to keep (per type) before rotating
MAX_BACKUPS = 30


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def backup_sqlite(backup_dir: str) -> str:
    """Copy SQLite database file."""
    if not os.path.exists(SQLITE_PATH):
        print("  SQLite database not found, skipping.")
        return None

    dest = os.path.join(backup_dir, f"wp200_sqlite_{timestamp()}.db")
    shutil.copy2(SQLITE_PATH, dest)
    size_mb = os.path.getsize(dest) / (1024 * 1024)
    print(f"  SQLite backup: {dest} ({size_mb:.2f} MB)")
    return dest


def backup_postgres(backup_dir: str) -> str:
    """Dump PostgreSQL database."""
    try:
        from app.core.config import settings
        if not settings.DATABASE_URL or "postgresql" not in settings.DATABASE_URL:
            print("  PostgreSQL not configured, skipping.")
            return None
    except Exception:
        print("  Could not load config, skipping PostgreSQL backup.")
        return None

    dest = os.path.join(backup_dir, f"wp200_postgres_{timestamp()}.sql")

    try:
        result = subprocess.run(
            ["pg_dump", settings.DATABASE_URL, "--no-owner", "--no-acl", "-f", dest],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            size_mb = os.path.getsize(dest) / (1024 * 1024)
            print(f"  PostgreSQL backup: {dest} ({size_mb:.2f} MB)")
            return dest
        else:
            print(f"  pg_dump failed: {result.stderr[:200]}")
            return None
    except FileNotFoundError:
        print("  pg_dump not found (PostgreSQL client tools not installed)")
        return None
    except Exception as e:
        print(f"  PostgreSQL backup failed: {e}")
        return None


def backup_data_dir(backup_dir: str) -> str:
    """Archive the entire data directory."""
    if not os.path.exists(DATA_DIR):
        print("  Data directory not found, skipping.")
        return None

    dest = os.path.join(backup_dir, f"wp200_data_{timestamp()}")
    shutil.make_archive(dest, "zip", DATA_DIR)
    dest_zip = dest + ".zip"
    size_mb = os.path.getsize(dest_zip) / (1024 * 1024)
    print(f"  Data archive: {dest_zip} ({size_mb:.2f} MB)")
    return dest_zip


def rotate_backups(backup_dir: str, prefix: str, max_keep: int = MAX_BACKUPS):
    """Delete oldest backups beyond max_keep."""
    files = sorted([
        f for f in os.listdir(backup_dir)
        if f.startswith(prefix)
    ])
    if len(files) > max_keep:
        to_delete = files[:len(files) - max_keep]
        for f in to_delete:
            path = os.path.join(backup_dir, f)
            os.remove(path)
            print(f"  Rotated old backup: {f}")


def main():
    parser = argparse.ArgumentParser(description="WP-200 Database Backup")
    parser.add_argument(
        "--backup-dir", default=DEFAULT_BACKUP_DIR,
        help="Directory to store backups (e.g., OneDrive/Google Drive folder)"
    )
    args = parser.parse_args()

    backup_dir = os.path.abspath(args.backup_dir)
    os.makedirs(backup_dir, exist_ok=True)

    print(f"{'=' * 60}")
    print(f"WP-200 Backup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backup directory: {backup_dir}")
    print(f"{'=' * 60}")

    print("\n1. Backing up SQLite database...")
    backup_sqlite(backup_dir)

    print("\n2. Backing up PostgreSQL database...")
    backup_postgres(backup_dir)

    print("\n3. Backing up data directory...")
    backup_data_dir(backup_dir)

    print("\n4. Rotating old backups...")
    rotate_backups(backup_dir, "wp200_sqlite_")
    rotate_backups(backup_dir, "wp200_postgres_")
    rotate_backups(backup_dir, "wp200_data_")

    print(f"\nBackup complete. Files in: {backup_dir}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
