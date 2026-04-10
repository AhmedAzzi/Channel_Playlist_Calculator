@echo off
echo Starting YouTube Playlist Calc...

:: Start the Python backend in a new window
echo Starting Backend Server...
start cmd /k "python server.py"

:: Start the Frontend dev server
echo Starting Frontend Development Server...
cd frontend
npm run dev

pause
