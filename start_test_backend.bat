@echo off
cd /d C:\REIMS
echo Starting Test Backend on Port 8002...
C:\REIMS\queue_service\venv\Scripts\python.exe test_backend_simple.py
pause