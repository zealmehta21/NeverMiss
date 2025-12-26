"""
Signup page
"""
import streamlit as st
from database import sign_up, get_current_user

# Page configuration
st.set_page_config(
    page_title="NeverMiss - Sign Up",
    page_icon="✅"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=DM+Sans:wght@400;500;700&display=swap');
    
    .main {
        background-color: #FFFDFA;
    }
    
    h1, h2 {
        font-family: 'Libre Baskerville', serif;
        color: #5C4E3D;
    }
    
    body {
        font-family: 'DM Sans', sans-serif;
        color: #454240;
    }
    
    /* Primary button color: #b88e23 */
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

# Check if already logged in
user = get_current_user()
if user and user.user:
    st.switch_page("pages/2_Main_App.py")

st.title("Create Your NeverMiss Account")

# Signup form
with st.form("signup_form"):
    email = st.text_input("Email", placeholder="your@email.com")
    password = st.text_input("Password", type="password", placeholder="Choose a strong password")
    password_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
    
    submit = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
    
    if submit:
        if not email or not password:
            st.error("Please fill in all fields")
        elif password != password_confirm:
            st.error("Passwords do not match")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters")
        else:
            try:
                result = sign_up(email, password)
                if result:
                    # Check if session was returned (no email confirmation required)
                    if result.get("session"):
                        st.success("Account created successfully! Logging you in...")
                        st.switch_page("pages/2_Main_App.py")
                    else:
                        # Email confirmation required
                        st.info("Account created! Please check your email to confirm your account before logging in.")
                        st.switch_page("pages/4_Login.py")
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("Already have an account? Log in", use_container_width=True, key="login_from_signup"):
        st.switch_page("pages/4_Login.py")
with col2:
    if st.button("Forgot password?", use_container_width=True, key="forgot_pwd_signup"):
        st.switch_page("pages/5_Reset_Password.py")
if st.button("Back to Home", use_container_width=True, key="home_from_signup"):
    st.switch_page("pages/1_NeverMiss.py")
