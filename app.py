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
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": "Your EverAge Longevity Plan 📄"
            }
        ],
        "from": {
            "email": st.secrets["sendgrid"]["from_email"]
        },
        "content": [
            {
                "type": "text/plain",
                "value": "Hi! Here’s your personalized EverAge longevity plan attached as a PDF. 🙊"
            }
        ],
        "attachments": [
            {
                "content": file_data,
                "type": "application/pdf",
                "filename": "longevity_plan.pdf"
            }
        ]
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

# === Inside Tab 4: Replace Existing Code ===
# --- Tab 4 ---
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
