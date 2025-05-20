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

# ========== SAFE RERUN FIX ==========
if st.session_state.get('_rerun_trigger'):
    st.session_state._rerun_trigger = False
    st.experimental_rerun()

# ... rest of your code follows ...

# In run_onboarding(), replace st.experimental_rerun() with:
# st.session_state._rerun_trigger = True
# st.stop()

# Make sure you update this line in your code block accordingly.
