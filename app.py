import streamlit as st

st.set_page_config(
    page_title="EverAge | Longevity Copilot",
    page_icon="🧬",
    layout="wide"
)

# ========== LANDING PAGE ==========
st.image("static/everage_full_logo.png", width=260)

st.markdown("""
<h1 style='text-align: center; color: #0A7E8C; font-size: 2.5em;'>Live Smarter. Live Longer.</h1>
<p style='text-align: center; font-size: 1.2em; color: #444;'>
EverAge is your AI-powered longevity copilot. Personalized plans. Smart health habits. All in one place.
</p>
""", unsafe_allow_html=True)

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
