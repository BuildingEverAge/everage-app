@echo off
git add .
git commit -m "%*"
git push

echo.
echo ✅ Git push complete. Starting Streamlit and opening browser...
echo.

start http://localhost:8501
streamlit run app.py
