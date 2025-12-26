"""
Login page
"""
import streamlit as st
from database import sign_in, get_current_user

# Page configuration
st.set_page_config(
    page_title="NeverMiss - Login",
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

st.title("Log in to NeverMiss")

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
    st.switch_page("pages/1_NeverMiss.py")
