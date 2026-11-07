@echo off
set FOOTBALL_API_KEY=cdf43a1758a94f9883a6ca3d8d39f41d
pip install -r requirements.txt
start http://127.0.0.1:8000
uvicorn main:app --reload
