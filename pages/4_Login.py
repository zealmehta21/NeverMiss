"""
Login page
"""
import streamlit as st
from database import sign_in, get_current_user

# Page configuration
st.set_page_config(
    page_title="Skkadoosh - Login",
    page_icon="✅"
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
        --button-primary: #ff4b4b;
        --button-primary-hover: #e63946;
    }
    
    /* CSS Variables for Dark Theme */
    [data-theme="dark"] {
        --bg-color: #1a1a1a;
        --text-color: #e0e0e0;
        --heading-color: #ffffff;
        --button-primary: #ff4b4b;
        --button-primary-hover: #ff6b6b;
    }
    
    .main {
        background-color: var(--bg-color) !important;
    }
    
    body {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        font-family: 'DM Sans', sans-serif;
    }
    
    h1, h2 {
        font-family: 'Libre Baskerville', serif;
        color: var(--heading-color) !important;
    }
    
    .stTextInput>div>div>input,
    .stTextInput>div>div>input:focus {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
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

# Check if already logged in
user = get_current_user()
if user and user.user:
    st.switch_page("pages/2_Main_App.py")

st.title("Log in to Skkadoosh")

# Login form
with st.form("login_form"):
    email = st.text_input("Email", placeholder="your@email.com")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    submit = st.form_submit_button("Log In", type="primary", use_container_width=True)
    
    if submit:
        if not email or not password:
            st.error("Please fill in all fields")
        else:
            try:
                result = sign_in(email, password)
                if result:
                    st.success("Logged in successfully!")
                    st.switch_page("pages/2_Main_App.py")
            except Exception as e:
                st.error(f"Error logging in: {str(e)}")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("Forgot password?", use_container_width=True, key="forgot_pwd_login"):
        st.switch_page("pages/5_Reset_Password.py")
with col2:
    if st.button("Don't have an account? Sign up", use_container_width=True, key="signup_from_login"):
        st.switch_page("pages/3_Signup.py")
if st.button("Back to Home", use_container_width=True, key="home_from_login"):
    st.switch_page("pages/1_Skkadoosh.py")
