@echo off
git add .
git commit -m "%*"
git push

echo.
echo ✅ Code pushed. Opening Streamlit Cloud...
start https://everage.streamlit.app/