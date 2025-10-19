@echo off
echo Starting REIMS Frontend...
cd frontend
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)
echo Starting Vite development server...
echo Frontend will be available at: http://localhost:3000
npm run dev

















