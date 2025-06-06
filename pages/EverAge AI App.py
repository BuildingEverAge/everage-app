import streamlit as st
import openai
from datetime import datetime
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

# ========== PUBLIC PREVIEW MODE SUPPORT ==========
if st.session_state.get("demo_mode"):
    st.warning("🔓 You are using a public preview mode. Data won’t be saved.")
    username = "demo_user"
    user_data = {}
else:
    username = st.session_state.get("username", "")
    if not username:
        st.error("🚫 Please login from the main page.")
        st.stop()


# ========== CUSTOM UI STYLE ==========
st.markdown("""
<style>
/* Global font and body */
body {
    font-family: 'Segoe UI', sans-serif;
}

/* Page title */
h1 {
    font-size: 2.2em !important;
    color: #0A7E8C;
}

/* Section headers */
h2, h3, .stMarkdown h3 {
    color: #157575;
    margin-top: 1em;
    margin-bottom: 0.5em;
}

/* Sidebar styling */
.css-1d391kg {
    background-color: #f5f9fa !important;
    padding: 1rem !important;
    border-radius: 12px !important;
}

/* Button style override */
div.stButton > button {
    background-color: #0A7E8C;
    color: white;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: bold;
    border: none;
    transition: all 0.3s ease;
}
div.stButton > button:hover {
    background-color: #0E99A5;
}

/* Input boxes */
.stTextInput input, .stTextArea textarea {
    border-radius: 8px !important;
    border: 1px solid #d0dfe4 !important;
    padding: 0.4rem 0.6rem !important;
}

/* Tabs */
.css-1hynsf2 {
    background-color: #eaf4f5;
    padding: 1rem;
    border-radius: 12px;
}

/* Section separator */
hr {
    border-top: 1px solid #ccc;
    margin-top: 2rem;
    margin-bottom: 2rem;
}
</style>
<h3 style='text-align: center; color: #157575; font-style: italic; margin-top: 0.5em;'>
Live Smarter. Live Longer.
</h3>
""", unsafe_allow_html=True)



# ========== SAFE RERUN FIX ==========
if "_rerun_trigger" in st.session_state and st.session_state._rerun_trigger:
    st.session_state._rerun_trigger = False
    st.rerun()

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

# ========== PLAN HISTORY VIEWER ==========
if st.session_state.get("history"):
    st.markdown("### 📜 View Previous Plans")
    selected_index = st.selectbox("Select a Plan", list(range(len(st.session_state.history))), format_func=lambda i: f"Plan {i + 1}")
    st.markdown(st.session_state.history[selected_index])

# ========== STREAK MILESTONE CELEBRATION FIX ==========
# Replace inside Progress tab loop
# Example:
# for h, s in streaks.items():
    



# ========== USER LOGIN ==========
st.sidebar.title("🔐 EverAge Login")
username_input = st.sidebar.text_input("Enter your email or username").strip().lower()
if username_input:
    st.session_state.username = username_input
username = st.session_state.get("username", "")
if not username:
    st.warning("Please log in from the sidebar to continue.")
    st.stop()
st.markdown(f"👋 Hello, **{username}**! Let’s keep you living long and strong.")


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
    return load_all_user_data().get(username, {}) or {}

def save_user_data(user_data):
    all_data = load_all_user_data()
    all_data[username] = user_data
    save_all_user_data(all_data)

# ========== SESSION STATE INIT ==========
user_data = load_user_data()
st.session_state.setdefault("onboarding_complete", user_data.get("onboarding_complete", False))
st.session_state.setdefault("onboarding_step", 0)
st.session_state.setdefault("history", user_data.get("history", []))
st.session_state.setdefault("habits", user_data.get("habits", []))
st.session_state.setdefault("scores", user_data.get("scores", {}))
st.session_state.setdefault("checkins", user_data.get("checkins", []))
st.session_state.setdefault("user_email", user_data.get("user_email", ""))

# ========== ONBOARDING FLOW ==========
def run_onboarding():
    st.title("👋 Welcome to EverAge")
    st.markdown("Let's personalize your experience with a few quick questions.")
    step = st.session_state.get("onboarding_step", 0)

    if step == 0:
        st.session_state.name = st.text_input("What's your name?")
        if st.button("Next") and st.session_state.name:
            st.session_state.onboarding_step = 1

    elif step == 1:
        st.session_state.age = st.number_input("Your Age", min_value=18, max_value=100, value=30)
        st.session_state.gender = st.selectbox("Gender (optional)", ["Prefer not to say", "Male", "Female", "Other"])
        if st.button("Next"):
            st.session_state.onboarding_step = 2

    elif step == 2:
        st.session_state.activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
        st.session_state.sleep = st.selectbox("Sleep Quality", ["Poor", "Average", "Good"])
        st.session_state.stress = st.selectbox("Stress Level", ["High", "Moderate", "Low"])
        st.session_state.diet = st.selectbox("Diet Type", ["Standard", "Vegetarian", "Keto", "Mediterranean"])
        if st.button("Next"):
            st.session_state.onboarding_step = 3

    elif step == 3:
        st.session_state.goals = st.text_area("Describe your main health and longevity goals")
        st.session_state.user_email = st.text_input("Your Email", value=st.session_state.user_email)
        if st.button("Finish") and st.session_state.goals and st.session_state.user_email:
            profile = {
                "name": st.session_state.name,
                "age": st.session_state.age,
                "gender": st.session_state.gender,
                "activity": st.session_state.activity,
                "sleep": st.session_state.sleep,
                "stress": st.session_state.stress,
                "diet": st.session_state.diet,
                "goals": st.session_state.goals,
                "user_email": st.session_state.user_email,
                "onboarding_complete": True
            }
            save_user_data({**user_data, **profile})
            st.session_state.onboarding_complete = True
            st.session_state._rerun_trigger = True
            st.rerun()

if not st.session_state.onboarding_complete:
    run_onboarding()
    st.stop()


# ========== UI FEEDBACK ENHANCEMENTS ==========
def show_plan_feedback():
    st.success("✅ Plan created!")
    st.toast("✅ Plan successfully generated!")
    if len(st.session_state.history) == 1:
        st.balloons()

def show_checkin_success():
    st.success("📌 Check-in saved! Great job staying consistent 💪")

def show_score_metrics(scores):
    cols = st.columns(len(scores))
    for i, (k, v) in enumerate(scores.items()):
        with cols[i]:
            st.metric(label=k, value=f"{v}/100")

# ====== MAIN TABS, TRACKER, PLAN, PROGRESS, EXPORT CONTINUE BELOW ======
# ✅ Let me know when you're ready to re-merge the full functionality.


# ========== SIDEBAR PROFILE ==========
st.sidebar.image("static/everage_icon.png", width=80)  # 🌀 Icon-only logo
st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Your Profile")
st.sidebar.markdown(f"**👤 Name:** {user_data.get('name', 'N/A')}")
st.sidebar.markdown(f"**🎂 Age:** {user_data.get('age', 'N/A')}")
st.sidebar.markdown(f"**🎯 Goals:** {user_data.get('goals', 'N/A')}")

if st.sidebar.button("✏️ Edit Profile"):
    st.session_state.onboarding_complete = False
    st.session_state.onboarding_step = 0
    st.session_state._rerun_trigger = True

# ========== MAIN SCREEN LOGO ==========
st.image("static/everage_full_logo.png", width=300)  # 🧬 Full logo on homepage





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

# ========== MAIN TABS ==========
st.title("🧬 EverAge: Your Longevity Copilot")
tabs = st.tabs(["📝 Create Plan", "✅ Tracker", "📈 Progress", "📄 Export"])

# --- Tab 1: Create Plan ---
with tabs[0]:
    st.subheader("Tell us about yourself 🧠")
    age = st.number_input("Age", min_value=18, max_value=100, value=user_data.get("age", 30))
    activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"], index=["Low", "Moderate", "High"].index(user_data.get("activity", "Moderate")))
    sleep = st.selectbox("Sleep Quality", ["Poor", "Average", "Good"], index=["Poor", "Average", "Good"].index(user_data.get("sleep", "Average")))
    stress = st.selectbox("Stress Level", ["High", "Moderate", "Low"], index=["High", "Moderate", "Low"].index(user_data.get("stress", "Moderate")))
    diet = st.selectbox("Diet Type", ["Standard", "Vegetarian", "Keto", "Mediterranean"], index=["Standard", "Vegetarian", "Keto", "Mediterranean"].index(user_data.get("diet", "Standard")))
    goals = st.text_area("Health Goals", value=user_data.get("goals", ""))
    email = st.text_input("Your Email", value=st.session_state.user_email)

    if st.button("🧪 Generate My Longevity Plan"):
        prompt = f"Age: {age}, Activity: {activity}, Sleep: {sleep}, Stress: {stress}, Diet: {diet}, Goals: {goals}"
        plan = get_ai_plan(prompt)
        st.session_state.history.append(plan)
        st.session_state.habits = extract_habits(plan)
        st.session_state.scores = calculate_scores(prompt)
        st.session_state.user_email = email
        save_user_data({
            **user_data,
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

# --- Tab 2: Daily Tracker ---
with tabs[1]:
    st.subheader("🗓️ Daily Check-in")
    if st.session_state.habits:
        today = datetime.now().strftime("%Y-%m-%d")
        checks = [st.checkbox(h, key=f"chk_{i}") for i, h in enumerate(st.session_state.habits)]
        if st.button("Submit Today’s Check-in"):
            st.session_state.checkins.append({"date": today, "checked": checks})
            save_user_data({
                **user_data,
                "history": st.session_state.history,
                "habits": st.session_state.habits,
                "scores": st.session_state.scores,
                "checkins": st.session_state.checkins,
                "user_email": st.session_state.user_email
            })
            st.success("📌 Check-in saved!")
    else:
        st.info("Please generate a plan first.")

# --- Tab 3: Progress ---
with tabs[2]:
    st.subheader("📈 Weekly Progress")
    
    if not st.session_state.checkins:
        st.info("No check-ins yet.")
    else:
        labels = [c["date"] for c in st.session_state.checkins]
        values = [sum(c["checked"]) for c in st.session_state.checkins]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(labels, values)
        ax.set_title("📊 Weekly Habit Progress")
        ax.set_ylabel("Habits Completed")
        ax.set_ylim(0, 5)
        ax.set_xticklabels(labels, rotation=45)
        st.pyplot(fig)

    if st.session_state.scores:
        st.markdown("**🧠 Health Scores:**")
        for k, v in st.session_state.scores.items():
            st.progress(v / 100, text=f"{k}: {v}")

    if st.session_state.habits:
        streaks = calculate_streaks(st.session_state.checkins, st.session_state.habits)
        st.subheader("🔥 Habit Streaks")
        for h, s in streaks.items():
            if s['current'] == 3:
                st.success(f"🔥 You're on a 3-day streak for **{h}**! Keep it up!")
            st.markdown(f"**{h}** — Current: {s['current']} 🔁 | Best: {s['best']} 🏆")




# --- Tab 4: Export Plan ---
with tabs[3]:
    st.subheader("📄 Export Plan")
    if st.session_state.history:
        latest_plan = st.session_state.history[-1]
        pdf = FPDF()
        pdf.add_page()

        # 🧬 Small top-right logo
        logo_width = 30
        margin_right = 10
        margin_top = 8
        page_width = pdf.w
        logo_x = page_width - logo_width - margin_right
        pdf.image("static/everage_full_logo.png", x=logo_x, y=margin_top, w=logo_width)

        # 📝 Content below
        pdf.set_y(28)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, latest_plan)
        pdf_path = "longevity_plan.pdf"
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


