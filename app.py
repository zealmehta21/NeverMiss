"""
Main entry point for NeverMiss app
Redirects to landing page by default
"""
import streamlit as st
from database import get_current_user

# Page configuration
st.set_page_config(
    page_title="NeverMiss",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Check if user is logged in, redirect accordingly
user = get_current_user()
if user and user.user:
    st.switch_page("pages/2_Main_App.py")
else:
    st.switch_page("pages/1_NeverMiss.py")