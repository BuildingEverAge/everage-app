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

# ========== LOGIN PANEL ==========
st.sidebar.title("🔐 EverAge Login")
username = st.sidebar.text_input("Enter your email or username").strip().lower()
if not username:
    st.warning("Please log in from the sidebar to continue.")
    st.stop()

# ========== USER DATA HANDLING ==========
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

# ========== SESSION STATE INIT ==========
user_data = load_user_data()
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
    habits = [line.strip("\u2022-• ").strip() for line in response.choices[0].message.content.strip().split("\n") if line.strip()]
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
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="longevity_plan.pdf">\ud83d\udcc4 Download Plan as PDF</a>'
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
    ax.set_title("\ud83d\udcca Weekly Habit Progress")
    ax.set_ylim(0, 5)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45)
    st.pyplot(fig)

# ========== UI ==========
st.title("\ud83e\uddec EverAge: Your Longevity Copilot")
tabs = st.tabs(["\ud83d\udcdd Create Plan", "\u2705 Daily Tracker", "\ud83d\udcc8 Progress", "\ud83d\udcc4 Export Plan"])

# --- Tab 1 ---
with tabs[0]:
    st.subheader("Tell us about yourself \ud83e\udde0")
    age = st.number_input("Age", min_value=18, max_value=100)
    activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
    sleep = st.selectbox("Sleep Quality", ["Poor", "Average", "Good"])
    stress = st.selectbox("Stress Level", ["High", "Moderate", "Low"])
    diet = st.selectbox("Diet Type", ["Standard", "Vegetarian", "Keto", "Mediterranean"])
    goals = st.text_area("Describe your longevity/health goals")

    if st.button("\ud83e\uddea Generate My Longevity Plan"):
        prompt = f"Age: {age}, Activity: {activity}, Sleep: {sleep}, Stress: {stress}, Diet: {diet}, Goals: {goals}"
        plan = get_ai_plan(prompt)
        st.session_state.history.append(plan)
        st.session_state.habits = extract_habits(plan)
        st.session_state.scores = calculate_scores(prompt)
        save_user_data({
            "history": st.session_state.history,
            "habits": st.session_state.habits,
            "scores": st.session_state.scores,
            "checkins": st.session_state.checkins
        })
        st.success("\u2705 Plan created!")
        st.markdown(plan)

# --- Tab 2 ---
with tabs[1]:
    st.subheader("\ud83d\uddd3 Track Today’s Habits")
    if st.session_state.habits:
        today = datetime.now().strftime("%Y-%m-%d")
        checks = [st.checkbox(habit) for habit in st.session_state.habits]
        if st.button("Submit Today’s Check-in"):
            st.session_state.checkins.append({"date": today, "checked": checks})
            save_user_data({
                "history": st.session_state.history,
                "habits": st.session_state.habits,
                "scores": st.session_state.scores,
                "checkins": st.session_state.checkins
            })
            st.success("\ud83d\udccc Logged successfully!")
    else:
        st.info("Please generate a plan to track habits.")

# --- Tab 3 ---
with tabs[2]:
    st.subheader("\ud83d\udcc8 Weekly Progress")
    show_progress_chart()
    if st.session_state.scores:
        st.markdown("**\ud83e\udde0 Health Scores (0–100):**")
        for k, v in st.session_state.scores.items():
            st.progress(v / 100, text=f"{k}: {v}")
    if st.session_state.habits:
        st.subheader("\ud83d\udd25 Habit Streaks")
        streaks = calculate_streaks(st.session_state.checkins, st.session_state.habits)
        for habit, data in streaks.items():
            st.markdown(f"**{habit}** — Current: {data['current']} \ud83d\udd01 | Best: {data['best']} \ud83c\udfc6")

# --- Tab 4 ---
with tabs[3]:
    st.subheader("\ud83d\udcc4 Download Your Plan")
    if st.session_state.history:
        latest_plan = st.session_state.history[-1]
        st.markdown(generate_pdf(latest_plan), unsafe_allow_html=True)
    else:
        st.info("No plan to export yet.")
