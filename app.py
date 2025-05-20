### ✅ Updated EverAge App with:
# - Regenerate/Edit Plan button
# - Improved UI structure and layout
# - Email saved to user data
# - Plan generation reuses current inputs
# - Ready for future onboarding and export

# START OF FILE

import streamlit as st
import openai
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
import json
import os
import requests

# ========== CONFIGURATION ==========
openai.api_key = st.secrets["openai"]["api_key"]
st.set_page_config(page_title="EverAge: Longevity Copilot", layout="wide")

DATA_FILE = "data/user_data.json"

# ========== EMAIL FUNCTION ==========
def send_email_with_pdf(to_email, pdf_path):
    with open(pdf_path, "rb") as f:
        file_data = base64.b64encode(f.read()).decode()

    data = {
        "personalizations": [{
            "to": [{"email": to_email}],
            "subject": "Your EverAge Longevity Plan 📄"
        }],
        "from": {
            "email": st.secrets["sendgrid"]["from_email"]
        },
        "content": [{
            "type": "text/plain",
            "value": "Hi! Here’s your personalized EverAge longevity plan attached as a PDF. 🙊"
        }],
        "attachments": [{
            "content": file_data,
            "type": "application/pdf",
            "filename": "longevity_plan.pdf"
        }]
    }

    response = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {st.secrets['sendgrid']['api_key']}",
            "Content-Type": "application/json"
        },
        json=data
    )
    return response.status_code == 202

# ========== USER LOGIN & DATA ==========
st.image("static/everage_logo.png", width=300)
st.sidebar.title("🔐 EverAge Login")
username = st.sidebar.text_input("Enter your email or username").strip().lower()
if not username:
    st.warning("Please log in from the sidebar to continue.")
    st.stop()

# ========== DATA LOAD/SAVE ==========
def load_all_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_all_user_data(all_data):
    with open(DATA_FILE, "w") as f:
        json.dump(all_data, f, indent=2)

def load_user_data():
    all_data = load_all_user_data()
    return all_data.get(username, {})

def save_user_data(user_data):
    all_data = load_all_user_data()
    all_data[username] = user_data
    save_all_user_data(all_data)

# ========== SESSION INIT ==========
user_data = load_user_data()
st.session_state.setdefault("history", user_data.get("history", []))
st.session_state.setdefault("habits", user_data.get("habits", []))
st.session_state.setdefault("scores", user_data.get("scores", {}))
st.session_state.setdefault("checkins", user_data.get("checkins", []))
st.session_state.setdefault("user_email", user_data.get("user_email", ""))

# ========== AI FUNCTIONS ==========
def get_ai_plan(prompt):
    structured_prompt = f"{prompt}\n\nPlease return a clearly formatted longevity plan with these sections:\n- Sleep\n- Exercise\n- Diet\n- Stress Management\nInclude 5 daily habits in a section titled 'Daily Habits'."
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a longevity coach..."},
            {"role": "user", "content": structured_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def extract_habits(plan_text):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Extract exactly 5 clear habits."},
            {"role": "user", "content": plan_text}
        ]
    )
    return [line.strip("•- ").strip() for line in response.choices[0].message.content.strip().split("\n") if line.strip()][:5]

def calculate_scores(prompt):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Score Sleep, Diet, Exercise, Stress (0-100)."},
            {"role": "user", "content": prompt}
        ]
    )
    lines = response.choices[0].message.content.split("\n")
    scores = {}
    for line in lines:
        if ":" in line:
            k, v = line.split(":", 1)
            try:
                scores[k.strip()] = int(v.strip())
            except:
                pass
    return scores

def calculate_streaks(checkins, habits):
    streaks = {h: {"current": 0, "best": 0} for h in habits}
    log = {h: [] for h in habits}
    for entry in checkins:
        d = datetime.strptime(entry["date"], "%Y-%m-%d").date()
        for i, done in enumerate(entry["checked"]):
            log[habits[i]].append((d, done))
    for h, l in log.items():
        l.sort()
        cur = best = 0
        prev = None
        for d, done in l:
            if done:
                cur = cur + 1 if prev and (d - prev).days == 1 else 1
                best = max(best, cur)
            else:
                cur = 0
            prev = d
        streaks[h] = {"current": cur, "best": best}
    return streaks

# ========== PDF UTILS ==========
def generate_pdf(plan):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, plan)
    filename = "longevity_plan.pdf"
    pdf.output(filename)
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="longevity_plan.pdf">📄 Download Plan</a>'

# ========== CHART ==========
def show_progress_chart():
    if not st.session_state.checkins:
        st.info("No check-ins yet.")
        return
    labels = [c["date"] for c in st.session_state.checkins]
    values = [sum(c["checked"]) for c in st.session_state.checkins]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values)
    ax.set_title("📊 Weekly Habit Progress")
    ax.set_ylabel("Habits Completed")
    ax.set_ylim(0, 5)
    ax.set_xticklabels(labels, rotation=45)
    st.pyplot(fig)

# ========== UI ==========
st.title("🧬 EverAge: Your Longevity Copilot")
tabs = st.tabs(["📝 Create Plan", "✅ Tracker", "📈 Progress", "📄 Export"])

# --- Tab 1 ---
with tabs[0]:
    st.subheader("Tell us about yourself 🧠")
    age = st.number_input("Age", min_value=18, max_value=100)
    activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
    sleep = st.selectbox("Sleep Quality", ["Poor", "Average", "Good"])
    stress = st.selectbox("Stress Level", ["High", "Moderate", "Low"])
    diet = st.selectbox("Diet Type", ["Standard", "Vegetarian", "Keto", "Mediterranean"])
    goals = st.text_area("Health Goals")
    email = st.text_input("Your Email", value=st.session_state.user_email)

    if st.button("🧪 Generate My Longevity Plan"):
        prompt = f"Age: {age}, Activity: {activity}, Sleep: {sleep}, Stress: {stress}, Diet: {diet}, Goals: {goals}"
        plan = get_ai_plan(prompt)
        st.session_state.history.append(plan)
        st.session_state.habits = extract_habits(plan)
        st.session_state.scores = calculate_scores(prompt)
        st.session_state.user_email = email
        save_user_data({
            "history": st.session_state.history,
            "habits": st.session_state.habits,
            "scores": st.session_state.scores,
            "checkins": st.session_state.checkins,
            "user_email": email
        })
        st.success("✅ Plan created!")
        st.markdown(plan)

    if st.button("♻️ Regenerate My Plan") and st.session_state.history:
        prompt = f"Age: {age}, Activity: {activity}, Sleep: {sleep}, Stress: {stress}, Diet: {diet}, Goals: {goals}"
        plan = get_ai_plan(prompt)
        st.session_state.history[-1] = plan
        st.session_state.habits = extract_habits(plan)
        st.session_state.scores = calculate_scores(prompt)
        st.markdown(plan)

# --- Tab 2 ---
with tabs[1]:
    st.subheader("🗓️ Daily Check-in")
    if st.session_state.habits:
        today = datetime.now().strftime("%Y-%m-%d")
        checks = [st.checkbox(h, key=f"chk_{i}") for i, h in enumerate(st.session_state.habits)]
        if st.button("Submit Today’s Check-in"):
            st.session_state.checkins.append({"date": today, "checked": checks})
            save_user_data({
                "history": st.session_state.history,
                "habits": st.session_state.habits,
                "scores": st.session_state.scores,
                "checkins": st.session_state.checkins,
                "user_email": st.session_state.user_email
            })
            st.success("📌 Check-in saved!")
    else:
        st.info("Please generate a plan first.")

# --- Tab 3 ---
with tabs[2]:
    st.subheader("📈 Weekly Progress")
    show_progress_chart()
    if st.session_state.scores:
        st.markdown("**🧠 Health Scores:**")
        for k, v in st.session_state.scores.items():
            st.progress(v / 100, text=f"{k}: {v}")
    if st.session_state.habits:
        streaks = calculate_streaks(st.session_state.checkins, st.session_state.habits)
        st.subheader("🔥 Habit Streaks")
        for h, s in streaks.items():
            st.markdown(f"**{h}** — Current: {s['current']} 🔁 | Best: {s['best']} 🏆")

# --- Tab 4 ---
with tabs[3]:
    st.subheader("📄 Export Plan")
    if st.session_state.history:
        latest_plan = st.session_state.history[-1]
        pdf_path = "longevity_plan.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, latest_plan)
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="longevity_plan.pdf">📄 Download Plan as PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

        email_input = st.text_input("📬 Email to send to:", value=st.session_state.user_email)
        if st.button("Send Plan via Email"):
            if send_email_with_pdf(email_input, pdf_path):
                st.success("✅ Email sent!")
            else:
                st.error("❌ Email failed.")
    else:
        st.info("No plan available to export.")
