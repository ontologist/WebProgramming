@echo off
REM Copyright (c) 2026 Yuri Tijerino. All rights reserved.
REM 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
REM Unauthorized copying, modification, or distribution of this file is prohibited.
REM 本ファイルの無断複製、改変、配布を禁じます。
REM ============================================================
REM WP-200 Daily Backup - Windows Task Scheduler Setup
REM ============================================================
REM Run this script as Administrator to create a daily backup task.
REM Edit the paths below before running.
REM ============================================================

SET PYTHON_PATH=C:\path\to\WebProgramming\backend\venv\Scripts\python.exe
SET SCRIPT_PATH=C:\path\to\WebProgramming\backend\scripts\backup.py
SET WORKING_DIR=C:\path\to\WebProgramming\backend
SET BACKUP_DIR=D:\OneDrive\WP200-Backups

echo Creating scheduled task: WP200_Daily_Backup
echo Python: %PYTHON_PATH%
echo Script: %SCRIPT_PATH%
echo Backup dir: %BACKUP_DIR%
echo.

schtasks /create ^
  /tn "WP200_Daily_Backup" ^
  /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" --backup-dir \"%BACKUP_DIR%\"" ^
  /sc daily ^
  /st 02:00 ^
  /sd %date:~-4%/%date:~-10,2%/%date:~-7,2% ^
  /ru "%USERNAME%" ^
  /rl HIGHEST ^
  /f

echo.
echo Task created. It will run daily at 2:00 AM.
echo To verify: taskschd.msc -> Task Scheduler Library -> WP200_Daily_Backup
echo To run now: schtasks /run /tn "WP200_Daily_Backup"
pause
