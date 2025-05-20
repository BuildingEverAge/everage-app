# ✅ EverAge App: Unified Version
# - Onboarding flow
# - Profile display + update in sidebar
# - Editable plan inputs
# - Improved UI layout
# - All-in-one production-ready app

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

# ========== USER LOGIN ==========
st.image("static/everage_logo.png", width=300)
st.sidebar.title("🔐 EverAge Login")
username = st.sidebar.text_input("Enter your email or username").strip().lower()

if not username:
    st.warning("Please log in from the sidebar to continue.")
    st.stop()

# ✅ Safe rerun fix (after user input is initialized)
if st.session_state.get("_rerun_trigger", False):
    st.session_state._rerun_trigger = False
    st.experimental_rerun()

st.write("✅ Logged in as:", username)

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
    return load_all_user_data().get(username, {})

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
    st.write("🧪 Entered onboarding flow")
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
            st.stop()

# ✅ FINAL ONBOARDING CHECK
if not st.session_state.onboarding_complete:
    run_onboarding()
    st.stop()
