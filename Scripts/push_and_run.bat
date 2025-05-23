@echo off
git add .
git commit -m "%*"
git push
echo.
echo ✅ Git push complete. Starting Streamlit...
echo.
streamlit run app.py
