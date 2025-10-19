@echo off
REM ============================================================================
REM Quick Backup Script - Double-click to backup SQLite database
REM ============================================================================
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║          Quick REIMS Database Backup                             ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0backup_sqlite_database.ps1"

echo.
echo Press any key to close...
pause >nul

