import streamlit as st 
import openai
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
import json
import os

# ========== CONFIGURATION ==========
openai.api_key = st.secrets["openai"]["api_key"]
st.set_page_config(page_title="EverAge: Longevity Copilot", layout="wide")

DATA_FILE = "data/user_data.json"

# ========== LOGIN ==========
username = st.text_input("👤 Enter your username").strip().lower()
if not username:
    st.warning("Please enter a username to continue.")
    st.stop()

# ========== HELPER FUNCTIONS ==========
def load_user_data(username):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return data.get(username, {})
    return {}

def save_user_data(username, user_data):
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    data[username] = user_data
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def calculate_streaks(checkins, habits):
    streaks = {habit: {"current": 0, "best": 0} for habit in habits}
    habit_log = {habit: [] for habit in habits}

    for entry in checkins:
        date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
        for i, done in enumerate(entry["checked"]):
            habit = habits[i]
            habit_log[habit].append((date, done))

    for habit, logs in habit_log.items():
        logs.sort()
        current = best = 0
        previous_date = None
        for date, done in logs:
            if done:
                if previous_date and (date - previous_date).days == 1:
                    current += 1
                else:
                    current = 1
                best = max(best, current)
            else:
                current = 0
            previous_date = date
        streaks[habit]["current"] = current
        streaks[habit]["best"] = best

    return streaks

# ========== SESSION STATE INIT ==========
user_data = load_user_data(username)
if 'history' not in st.session_state:
    st.session_state.history = user_data.get("history", [])
if 'habits' not in st.session_state:
    st.session_state.habits = user_data.get("habits", [])
if 'scores' not in st.session_state:
    st.session_state.scores = user_data.get("scores", {})
if 'checkins' not in st.session_state:
    st.session_state.checkins = user_data.get("checkins", [])

# ========== AI FUNCTIONS ==========
def get_ai_plan(prompt):
    structured_prompt = (
        f"{prompt}\n\n"
        "Please return a clearly formatted longevity plan with the following sections:\n"
        "- Sleep\n- Exercise\n- Diet\n- Stress Management\n"
        "Also include 5 specific, practical daily habits in a separate section titled 'Daily Habits'."
    )
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a longevity coach. Create personalized health plans with clear structure and formatting."},
            {"role": "user", "content": structured_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def extract_habits(plan_text):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Extract exactly 5 clear, specific daily habits from this plan (no headers)."},
            {"role": "user", "content": plan_text}
        ]
    )
    habits = [line.strip("•-• ").strip() for line in response.choices[0].message.content.strip().split("\n") if line.strip()]
    return habits[:5]

def calculate_scores(prompt):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Score the user’s health habits (0-100) based on Sleep, Diet, Exercise, and Stress. Format each on a new line like: Sleep: 80"},
            {"role": "user", "content": prompt}
        ]
    )
    text = response.choices[0].message.content
    scores = {"Sleep": 0, "Diet": 0, "Exercise": 0, "Stress": 0}
    for line in text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            try:
                scores[key.strip()] = int(value.strip())
            except ValueError:
                continue
    return scores

# ========== PDF EXPORT ==========
def generate_pdf(plan):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, plan)
    filename = "longevity_plan.pdf"
    pdf.output(filename)
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="longevity_plan.pdf">📄 Download Plan as PDF</a>'
    return href

# ========== CHART ==========
def show_progress_chart():
    data = st.session_state.checkins
    if not data:
        st.info("No check-in data yet.")
        return
    labels = [d["date"] for d in data]
    values = [sum(d["checked"]) for d in data]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values, color='green')
    ax.set_ylabel("Habits Completed")
    ax.set_title("📊 Weekly Habit Progress")
    ax.set_ylim(0, 5)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45)
    st.pyplot(fig)

# ========== UI LAYOUT ==========
st.title("🧬 EverAge: Your Longevity Copilot")
tabs = st.tabs(["📝 Create Plan", "✅ Daily Tracker", "📊 Progress", "📄 Export Plan"])

# --- Tab 1: Plan Creation ---
with tabs[0]:
    st.subheader("Tell us about yourself 🧠")
    age = st.number_input("Age", min_value=18, max_value=100)
    activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
    sleep = st.selectbox("Sleep Quality", ["Poor", "Average", "Good"])
    stress = st.selectbox("Stress Level", ["High", "Moderate", "Low"])
    diet = st.selectbox("Diet Type", ["Standard", "Vegetarian", "Keto", "Mediterranean"])
    goals = st.text_area("Describe your longevity/health goals")

    if st.button("🧪 Generate My Longevity Plan"):
        prompt = f"Age: {age}, Activity: {activity}, Sleep: {sleep}, Stress: {stress}, Diet: {diet}, Goals: {goals}"
        plan = get_ai_plan(prompt)
        st.session_state.history.append(plan)
        st.session_state.habits = extract_habits(plan)
        st.session_state.scores = calculate_scores(prompt)
        save_user_data(username, {
            "history": st.session_state.history,
            "habits": st.session_state.habits,
            "scores": st.session_state.scores,
            "checkins": st.session_state.checkins
        })
        st.success("✅ Plan created!")
        st.markdown(plan)

# --- Tab 2: Daily Habit Tracker ---
with tabs[1]:
    st.subheader("📅 Track Today’s Habits")
    if st.session_state.habits:
        today = datetime.now().strftime("%Y-%m-%d")
        checks = [st.checkbox(habit) for habit in st.session_state.habits]
        if st.button("Submit Today’s Check-in"):
            st.session_state.checkins.append({"date": today, "checked": checks})
            save_user_data(username, {
                "history": st.session_state.history,
                "habits": st.session_state.habits,
                "scores": st.session_state.scores,
                "checkins": st.session_state.checkins
            })
            st.success("📌 Logged successfully!")
    else:
        st.info("Please generate a plan to track habits.")

# --- Tab 3: Weekly Progress ---
with tabs[2]:
    st.subheader("📈 Weekly Progress")
    show_progress_chart()
    if st.session_state.scores:
        st.markdown("**🧠 Health Scores (0–100):**")
        for k, v in st.session_state.scores.items():
            st.progress(v / 100, text=f"{k}: {v}")
    if st.session_state.habits:
        st.subheader("🔥 Habit Streaks")
        streaks = calculate_streaks(st.session_state.checkins, st.session_state.habits)
        for habit, data in streaks.items():
            st.markdown(f"**{habit}** — Current: {data['current']} 🔁 | Best: {data['best']} 🏆")

# --- Tab 4: Export ---
with tabs[3]:
    st.subheader("📄 Download Your Plan")
    if st.session_state.history:
        latest_plan = st.session_state.history[-1]
        st.markdown(generate_pdf(latest_plan), unsafe_allow_html=True)
    else:
        st.info("No plan to export yet.")
