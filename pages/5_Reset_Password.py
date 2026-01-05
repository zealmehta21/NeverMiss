"""
Reset Password page
"""
import streamlit as st
from database import reset_password_for_email, get_current_user

# Page configuration
st.set_page_config(
    page_title="Skkadoosh - Reset Password",
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

# Check if user is logged in
user = get_current_user()
is_logged_in = user and user.user

if is_logged_in:
    st.title("Change Password")
    st.info("To change your password, please use the password reset link sent to your email. You can request one below after logging out.")
    st.markdown("---")
    if st.button("Log Out", type="primary"):
        from database import sign_out
        sign_out()
        st.switch_page("pages/4_Login.py")
else:
st.title("Reset Password")
st.markdown("Enter your email address and we'll send you a password reset link.")

    # Reset password form (not logged in)
with st.form("reset_form"):
    email = st.text_input("Email", placeholder="your@email.com")
    
    submit = st.form_submit_button("Send Reset Link", type="primary", use_container_width=True)
    
    if submit:
        if not email:
            st.error("Please enter your email address")
        else:
            try:
                    reset_password_for_email(email)
                    st.success("Password reset link sent! Please check your email and follow the instructions to reset your password.")
                    st.info("Note: Make sure to check your spam folder if you don't see the email.")
            except Exception as e:
                st.error(f"Error sending reset link: {str(e)}")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("Remember your password? Log in", use_container_width=True, key="login_from_reset"):
        st.switch_page("pages/4_Login.py")
with col2:
    if st.button("Don't have an account? Sign up", use_container_width=True, key="signup_from_reset"):
        st.switch_page("pages/3_Signup.py")
if st.button("Back to Home", use_container_width=True, key="home_from_reset"):
    st.switch_page("pages/1_Skkadoosh.py")
