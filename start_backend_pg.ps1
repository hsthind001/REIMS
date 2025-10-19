$env:DATABASE_URL = 'postgresql://postgres:dev123@localhost:5432/reims'
Write-Host 'DATABASE_URL set to: ' $env:DATABASE_URL
cd C:\REIMS
python run_backend.py
