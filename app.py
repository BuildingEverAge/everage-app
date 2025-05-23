import streamlit as st

st.set_page_config(
    page_title="EverAge | Longevity Copilot",
    page_icon="🧬",
    layout="wide"
)

# ========== AUTO-REDIRECT IF LOGGED IN ==========
if st.session_state.get("username"):
    st.switch_page("pages/EverAge AI App.py")  # ✅ Redirect if logged in

# ========== LANDING PAGE ==========
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image("static/everage_full_logo.png", width=240)
st.markdown("""
    <h1 style='color: #0A7E8C; font-size: 2.5em; margin-bottom: 0.2em;'>Live Smarter. Live Longer.</h1>
    <p style='font-size: 1.2em; color: #444;'>Your AI-powered longevity copilot.</p>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

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

with col2:
    st.markdown("### 🚀 Ready to Start?")
    if st.button("Start EverAge AI App"):
        st.switch_page("pages/EverAge AI App.py")

    st.markdown("or")

    if st.button("🔍 Try Without Login"):
        st.session_state.username = "demo_user"
        st.session_state.demo_mode = True
        st.switch_page("pages/EverAge AI App.py")
