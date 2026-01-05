"""
Landing page for Skkadoosh
"""
import streamlit as st
from database import get_current_user

# Page configuration
st.set_page_config(
    page_title="Skkadoosh - Turn your voice into prioritized actions",
    page_icon="✅",
    layout="wide"
)

# Custom CSS with theme detection
st.markdown("""
<script>
    // Detect system theme preference
    function detectTheme() {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
        
        // Listen for theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
        });
    }
    
    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', detectTheme);
    } else {
        detectTheme();
    }
</script>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=DM+Sans:wght@400;500;700&display=swap');
    
    /* CSS Variables for Light Theme (default) */
    :root {
        --bg-color: #ffffff;
        --text-color: #454240;
        --heading-color: #333333;
        --task-bg: #ffffff;
        --button-primary: #ff4b4b;
        --button-primary-hover: #e63946;
        --border-color: #FF6B6B;
    }
    
    /* CSS Variables for Dark Theme */
    [data-theme="dark"] {
        --bg-color: #1a1a1a;
        --text-color: #e0e0e0;
        --heading-color: #ffffff;
        --task-bg: #2a2a2a;
        --button-primary: #ff4b4b;
        --button-primary-hover: #ff6b6b;
        --border-color: #FF6B6B;
    }
    
    .main {
        background-color: var(--bg-color) !important;
    }
    
    body {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        font-family: 'DM Sans', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Libre Baskerville', serif;
        color: var(--heading-color) !important;
    }
    
    .testimonial {
        background-color: var(--task-bg) !important;
        padding: 20px;
        border-left: 4px solid var(--border-color);
        margin: 20px 0;
        border-radius: 5px;
    }
    
    .cta-button {
        background-color: var(--button-primary);
        color: white;
        padding: 15px 30px;
        font-size: 18px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-family: 'DM Sans', sans-serif;
    }
    
    /* Primary button color */
    .stButton > button[kind="primary"],
    button[kind="primary"],
    [data-testid="baseButton-primary"] {
        background-color: var(--button-primary) !important;
        border-color: var(--button-primary) !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    button[kind="primary"]:hover,
    [data-testid="baseButton-primary"]:hover {
        background-color: var(--button-primary-hover) !important;
        border-color: var(--button-primary-hover) !important;
    }
    
    /* Completely hide sidebar and prevent any flash */
    section[data-testid="stSidebar"],
    div[data-testid="stSidebar"],
    .css-1d391kg,
    [data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        min-width: 0 !important;
    }
    
    /* Hide sidebar toggle button */
    button[data-testid="baseButton-header"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Check if user is already logged in
user = get_current_user()
if user and user.user:
    st.switch_page("pages/2_Main_App.py")

# Main content
st.markdown("# Turn your voice into prioritized actions")
st.markdown("### Skkadoosh")
st.markdown("""
    <div style="color: var(--text-color); font-size: 1.1em; line-height: 1.8;">
    How many opportunities have you missed because you forgot? How many commitments slipped through the cracks?
    <br><br>
    Skkadoosh surfaces what matters early, helping you stay on top of your tasks, reminders, commitments, ideas, and project notes.
    <br><br>
    Ready to never miss a task again?
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)  # Add spacing before button
btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    if st.button("Join here", type="primary", use_container_width=True, key="join_btn"):
        st.switch_page("pages/3_Signup.py")
with btn_col2:
    if st.button("Login", type="primary", use_container_width=True, key="login_btn"):
        st.switch_page("pages/4_Login.py")

st.markdown("---")

# Testimonials
st.markdown("""
<div style="text-align: center;">
    <h2>What users are saying</h2>
</div>
""", unsafe_allow_html=True)
st.markdown("")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="testimonial">
        <p style="font-style: italic; color: var(--text-color);">
            "Skkadoosh has transformed how I manage my tasks. I just speak what's on my mind, and it magically organizes everything for me. Game changer!"
        </p>
        <p style="font-weight: bold; color: var(--heading-color); margin-top: 10px;">
            — Sarah M., Product Manager
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="testimonial">
        <p style="font-style: italic; color: var(--text-color);">
            "The voice commands are incredible. I can mark things done, reschedule, and set priorities just by talking. It feels like the future."
        </p>
        <p style="font-weight: bold; color: var(--heading-color); margin-top: 10px;">
            — Michael R., Entrepreneur
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="testimonial">
        <p style="font-style: italic; color: var(--text-color);">
            "Finally, a task manager that understands how I think. The AI prioritization is spot-on, and I love the daily email reminders."
        </p>
        <p style="font-weight: bold; color: var(--heading-color); margin-top: 10px;">
            — Jennifer L., Consultant
        </p>
    </div>
    """, unsafe_allow_html=True)

