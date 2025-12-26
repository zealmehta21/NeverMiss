"""
Landing page for NeverMiss
"""
import streamlit as st
from database import get_current_user

# Page configuration
st.set_page_config(
    page_title="NeverMiss - Turn your voice into prioritized actions",
    page_icon="✅",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=DM+Sans:wght@400;500;700&display=swap');
    
    .main {
        background-color: #FFFDFA;
    }
    
    h1, h2, h3 {
        font-family: 'Libre Baskerville', serif;
        color: #5C4E3D;
    }
    
    body {
        font-family: 'DM Sans', sans-serif;
        color: #454240;
    }
    
    .testimonial {
        background-color: #FFFDFA;
        padding: 20px;
        border-left: 4px solid #B88E23;
        margin: 20px 0;
        border-radius: 5px;
    }
    
    .cta-button {
        background-color: #B88E23;
        color: white;
        padding: 15px 30px;
        font-size: 18px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-family: 'DM Sans', sans-serif;
    }
    
    /* Change primary button color from #ff4b4b to #b88e23 */
    .stButton > button[kind="primary"],
    button[kind="primary"],
    [data-testid="baseButton-primary"] {
        background-color: #b88e23 !important;
        border-color: #b88e23 !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    button[kind="primary"]:hover,
    [data-testid="baseButton-primary"]:hover {
        background-color: #a67d1f !important;
        border-color: #a67d1f !important;
    }
</style>
""", unsafe_allow_html=True)

# Check if user is already logged in
user = get_current_user()
if user and user.user:
    st.switch_page("pages/2_Main_App.py")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("# Turn your voice into prioritized actions")
    st.markdown("### NeverMiss")
    st.markdown("""
    <div style="color: #454240; font-size: 1.1em; line-height: 1.8;">
        How many opportunities have you missed because you forgot? How many commitments slipped through the cracks?
        <br><br>
        NeverMiss surfaces what matters early, helping you stay on top of your tasks, reminders, commitments, ideas, and project notes.
        <br><br>
        <strong>Speak or type</strong> your tasks naturally. Our AI converts your input into an organized, prioritized task list for today, this week, and upcoming.
        <br><br>
        Ready to never miss a task again?
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing before button
    if st.button("Join here", type="primary", use_container_width=True, key="join_btn"):
        st.switch_page("pages/3_Signup.py")

with col2:
    st.markdown("""
    <div style="padding: 20px;">
        <h3>What makes NeverMiss different?</h3>
        <ul style="color: #454240; font-size: 1em; line-height: 2;">
            <li>🎤 Voice-first task management</li>
            <li>🤖 AI-powered organization and prioritization</li>
            <li>📅 Smart scheduling and reminders</li>
            <li>📧 Daily email reminders</li>
            <li>⚡ Instant task updates</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

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
        <p style="font-style: italic; color: #454240;">
            "NeverMiss has transformed how I manage my tasks. I just speak what's on my mind, and it magically organizes everything for me. Game changer!"
        </p>
        <p style="font-weight: bold; color: #5C4E3D; margin-top: 10px;">
            — Sarah M., Product Manager
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="testimonial">
        <p style="font-style: italic; color: #454240;">
            "The voice commands are incredible. I can mark things done, reschedule, and set priorities just by talking. It feels like the future."
        </p>
        <p style="font-weight: bold; color: #5C4E3D; margin-top: 10px;">
            — Michael R., Entrepreneur
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="testimonial">
        <p style="font-style: italic; color: #454240;">
            "Finally, a task manager that understands how I think. The AI prioritization is spot-on, and I love the daily email reminders."
        </p>
        <p style="font-weight: bold; color: #5C4E3D; margin-top: 10px;">
            — Jennifer L., Consultant
        </p>
    </div>
    """, unsafe_allow_html=True)

