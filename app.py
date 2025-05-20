
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

# ========== UI ==========
st.image("static/everage_logo.png", width=300)
st.title("🧬 EverAge: Your Longevity Copilot")

tabs = st.tabs(["📝 Create Plan", "✅ Daily Tracker", "📈 Progress", "📄 Export Plan"])

# Dummy session state setup for testing visual
if 'history' not in st.session_state:
    st.session_state.history = ["Sample longevity plan here..."]
if 'checkins' not in st.session_state:
    st.session_state.checkins = []

# ========== Tab 4: Export & Email ==========
with tabs[3]:
    st.subheader("📄 Download & Email Your Plan")
    if st.session_state.history:
        latest_plan = st.session_state.history[-1]
        pdf_path = "longevity_plan.pdf"
        st.markdown(generate_pdf(latest_plan), unsafe_allow_html=True)

        email_input = st.text_input("📬 Enter your email to receive this plan:")
        if st.button("Send Plan via Email"):
            if send_email_with_pdf(email_input, pdf_path):
                st.success("✅ Email sent successfully!")
            else:
                st.error("❌ Failed to send email. Please try again.")
    else:
        st.info("No plan to export yet.")
