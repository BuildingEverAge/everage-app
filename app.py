import os
import json
import streamlit as st

# ========== AUTO-REDIRECT IF LOGGED IN ==========
if st.session_state.get("username"):
    st.switch_page("pages/EverAge AI App.py")

# ========== LANDING PAGE ==========
st.set_page_config(page_title="EverAge | Longevity Copilot", page_icon="🧬", layout="wide")

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image("static/everage_full_logo.png", width=240)
st.markdown("""
    <h1 style='color: #0A7E8C; font-size: 2.5em; margin-bottom: 0.2em;'>Live Smarter. Live Longer.</h1>
    <p style='font-size: 1.2em; color: #444;'>Your AI-powered longevity copilot.</p>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

import os

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### 🧠 What You Get")
    st.markdown("""
    - Personalized health & longevity plan  
    - Daily habit tracking  
    - Weekly progress analysis  
    - PDF + email reports  
    - All powered by GPT-4  
    """)

    gif_path = os.path.join("static", "demo.gif")
    if os.path.exists(gif_path):
        st.markdown("### 🔍 See EverAge in Action")
        st.image(gif_path, use_container_width=True)
    else:
        st.markdown("### 🔍 See EverAge in Action")
        st.info("🚫 Demo GIF not found. Please add 'demo.gif' to the static/ folder.")






with col2:
    st.markdown("### 🚀 Ready to Start?")
    if st.button("Start EverAge AI App"):
        st.session_state.username = "guest_user"
        st.session_state.demo_mode = False
        st.switch_page("pages/EverAge AI App.py")

    st.markdown("or")

    if st.button("🔍 Try Without Login"):
        st.session_state.username = "demo_user"
        st.session_state.demo_mode = True
        st.switch_page("pages/EverAge AI App.py")

    st.markdown("---")
    st.markdown("### 📬 Stay in the loop")
    email_input = st.text_input("Leave your email to get updates:")

    if st.button("📩 Notify Me"):
        if email_input and "@" in email_input:
            os.makedirs("data", exist_ok=True)
            email_file = "data/emails.json"
            if os.path.exists(email_file):
                with open(email_file, "r") as f:
                    emails = json.load(f)
            else:
                emails = []

            if email_input not in emails:
                emails.append(email_input)
                with open(email_file, "w") as f:
                    json.dump(emails, f, indent=2)
                st.success("✅ You’ll be the first to know!")
            else:
                st.info("📧 You already signed up!")
        else:
            st.warning("Please enter a valid email.")


