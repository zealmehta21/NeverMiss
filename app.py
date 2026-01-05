"""
Main entry point for Skkadoosh app
Redirects to landing page by default
"""
import streamlit as st
from database import get_current_user

# Page configuration
st.set_page_config(
    page_title="Skkadoosh",
    page_icon="✅",
    layout="wide"
)

# Completely hide sidebar with CSS - load immediately
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
    /* CSS Variables for Light Theme (default) */
    :root {
        --bg-color: #ffffff;
    }
    
    /* CSS Variables for Dark Theme */
    [data-theme="dark"] {
        --bg-color: #1a1a1a;
    }
    
    body {
        background-color: var(--bg-color) !important;
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

# Check if user is logged in, redirect accordingly
user = get_current_user()
if user and user.user:
    st.switch_page("pages/2_Main_App.py")
else:
    st.switch_page("pages/1_Skkadoosh.py")