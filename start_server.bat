@echo off
title BioVote - AI Face Detection Voting System
echo Starting BioVote Face Detection Voting System...
echo Web Portal: http://127.0.0.1:5000
echo Presentation: http://127.0.0.1:5000/presentation

if exist "C:\Users\ASUS\AppData\Local\Programs\Python\Python310\python.exe" (
    "C:\Users\ASUS\AppData\Local\Programs\Python\Python310\python.exe" app.py
) else (
    python app.py
)
pause
