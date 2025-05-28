import os
import json
import streamlit as st

# ========== AUTO-REDIRECT IF LOGGED IN ==========
if st.session_state.get("username"):
    st.switch_page("pages/EverAge AI App.py")

# ========== LANDING PAGE CONFIG ==========
st.set_page_config(page_title="EverAge | Longevity Copilot", page_icon="🧬", layout="wide")

# ========== BACKGROUND STYLE + FADE-IN ==========
st.markdown("""
    <style>
    .landing-container {
        background: linear-gradient(to bottom right, #f9f9ff, #e6f0ff);
        padding: 3rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        animation: fadeIn 1.2s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    <div class="landing-container">
""", unsafe_allow_html=True)

# ========== MAIN LOGO AND HEADER ==========
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image("static/everage_full_logo.png", width=240)
st.markdown("""
    <h1 style='color: #0A7E8C; font-size: 2.5em; margin-bottom: 0.2em;'>Live Smarter. Live Longer.</h1>
    <p style='font-size: 1.2em; color: #444;'>Your AI-powered longevity copilot.</p>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ========== LANDING CONTENT ==========
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
    st.markdown("### 🔍 See EverAge in Action")
    if os.path.exists(gif_path):
        st.image(gif_path, use_container_width=True)
    else:
        st.info("🚫 Demo GIF not found. Please add 'demo.gif' to the static/ folder.")

with col2:
    st.markdown("### 📬 Enter Your Email to Start")
    email_input = st.text_input("Your email address")

    valid_email = email_input and "@" in email_input

    if not valid_email:
        st.info("Please enter a valid email to continue.")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("Start EverAge AI App"):
            if valid_email:
                st.session_state.username = "guest_user"
                st.session_state.demo_mode = False

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

                st.switch_page("pages/EverAge AI App.py")
            else:
                st.warning("Enter a valid email to continue.")

    with col_b:
        if st.button("🔍 Try Without Login"):
            if valid_email:
                st.session_state.username = "demo_user"
                st.session_state.demo_mode = True

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

                st.switch_page("pages/EverAge AI App.py")
            else:
                st.warning("Enter a valid email to continue.")

# ========== TRUST BOOSTERS ==========
st.markdown("---")
st.markdown("### 🤝 Trusted Foundations")
st.markdown("""
- 🤖 **Powered by GPT-4**  
- 🇨🇭 **Made with ❤️ in Switzerland**  
- 🔒 **Privacy-first. No tracking. No ads.**  
""")

# ========== DYNAMIC TESTIMONIALS FROM FILE ==========
st.markdown("### 💬 What People Are Saying")
testimonial_file = "data/testimonials.json"
if os.path.exists(testimonial_file):
    with open(testimonial_file, "r") as f:
        testimonials = json.load(f)
    for t in testimonials:
        st.info(f"⭐️⭐️⭐️⭐️⭐️ *\"{t['quote']}\"* – {t['author']}")
else:
    st.info("⭐️⭐️⭐️⭐️⭐️ *\"EverAge helped me finally stick to my health habits. It’s like having a personal coach, but smarter.\"* – Test User")

# ========== AI TIPS BASED ON USER SESSION ==========
st.markdown("### 🧠 AI-Powered Suggestions")
if st.session_state.get("username") == "demo_user":
    st.warning("You're in demo mode. Tips are limited. Sign up to unlock full guidance.")
elif st.session_state.get("username"):
    st.success("✅ Welcome back! Based on your usage, EverAge will soon offer personalized nudges.")
else:
    st.info("Tips will be unlocked after using the app.")

# ========== CLOSE LANDING CONTAINER ==========
st.markdown("</div>", unsafe_allow_html=True)

