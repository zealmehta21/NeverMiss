"""
Dashboard - Chat-like interface for task management
"""
import streamlit as st
from database import (
    get_current_user, get_user_id, get_tasks, create_task, 
    update_task, mark_task_complete, delete_task, snooze_task,
    save_transcript, get_transcripts
)
from gemini_integration import parse_user_input
from audio_transcription import transcribe_audio_bytes
from utils import filter_tasks_by_view, group_tasks_by_date
from email_service import send_task_update_email
from datetime import datetime
import pytz

# Page configuration
st.set_page_config(
    page_title="Skkadoosh - Dashboard",
    page_icon="✅",
    layout="wide"
)

# Custom CSS with theme detection and timezone detection
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
    
    // Detect user timezone
    function detectTimezone() {
        try {
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            const timezoneOffset = new Date().getTimezoneOffset();
            // Store in a hidden input that Streamlit can read
            const timezoneInput = document.getElementById('user_timezone');
            if (timezoneInput) {
                timezoneInput.value = timezone;
            } else {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.id = 'user_timezone';
                input.name = 'user_timezone';
                input.value = timezone;
                document.body.appendChild(input);
            }
        } catch (e) {
            console.error('Error detecting timezone:', e);
        }
    }
    
    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            detectTheme();
            detectTimezone();
        });
    } else {
        detectTheme();
        detectTimezone();
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
        --mic-bg: #ffffff;
        --mic-icon-color: #ff4b4b;
        --mic-hover-bg: #f5f5f5;
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
        --mic-bg: #2a2a2a;
        --mic-icon-color: #ff6b6b;
        --mic-hover-bg: #3a3a3a;
    }
    
    .main {
        background-color: var(--bg-color) !important;
    }
    
    body {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Libre Baskerville', serif;
        color: var(--heading-color) !important;
    }
    
    body, .stTextInput>div>div>input {
        font-family: 'DM Sans', sans-serif;
        color: var(--text-color) !important;
    }
    
    .stTextInput>div>div>input {
        background-color: var(--bg-color) !important;
    }
    
    .task-item {
        background-color: var(--task-bg) !important;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid var(--border-color);
        border-radius: 5px;
    }
    
    .priority-p0 { border-left-color: #FF0000; }
    .priority-high { border-left-color: #FF6B6B; }
    .priority-medium { border-left-color: #ff4b4b; }
    .priority-low { border-left-color: #FFB3BA; }
    
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
    
    /* Adjust main content to use full width */
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Navigation header styling */
    .stButton > button {
        font-weight: 500;
        border-radius: 5px;
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
    
    /* Audio input styling - make microphone button visible and clickable in both themes */
    [data-testid="stAudioInput"] {
        background-color: var(--mic-bg) !important;
    }
    [data-testid="stAudioInput"] > div {
        background-color: var(--mic-bg) !important;
    }
    /* Hide the waveform timecode (00:00 duration display) */
    [data-testid="stAudioInputWaveformTimeCode"] {
        display: none !important;
    }
    /* Make button visible, clickable, and same height as text input */
    [data-testid="stAudioInput"] button {
        height: 38px !important;
        min-height: 38px !important;
        cursor: pointer !important;
        opacity: 1 !important;
        visibility: visible !important;
        pointer-events: auto !important;
        z-index: 100 !important;
        background-color: var(--mic-bg) !important;
        border: 1px solid var(--mic-icon-color) !important;
        color: var(--mic-icon-color) !important;
    }
    /* Microphone icon styling - ensure visibility in dark theme */
    [data-testid="stAudioInput"] button svg,
    [data-testid="stAudioInput"] button path {
        fill: var(--mic-icon-color) !important;
        stroke: var(--mic-icon-color) !important;
        color: var(--mic-icon-color) !important;
    }
    [data-testid="stAudioInput"] button:not(:disabled):hover {
        opacity: 0.9 !important;
        background-color: var(--mic-hover-bg) !important;
        border-color: var(--button-primary-hover) !important;
    }
    [data-testid="stAudioInput"] button:not(:disabled):hover svg,
    [data-testid="stAudioInput"] button:not(:disabled):hover path {
        fill: var(--button-primary-hover) !important;
        stroke: var(--button-primary-hover) !important;
    }
    [data-testid="stAudioInput"] button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }
    
    /* Additional dark theme support for Streamlit components */
    [data-theme="dark"] .stTextInput>div>div>input {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        border-color: #444 !important;
    }
    
    [data-theme="dark"] .stSelectbox>div>div>select {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
    }
    
    [data-theme="dark"] .stDateInput>div>div>input {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
    }
    
    [data-theme="dark"] .stTimeInput>div>div>input {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
    }
    
    [data-theme="dark"] .stTextArea>div>div>textarea {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        border-color: #444 !important;
    }
    
    /* Ensure microphone icon is always visible with high contrast */
    [data-theme="dark"] [data-testid="stAudioInput"] button {
        border: 2px solid var(--mic-icon-color) !important;
        box-shadow: 0 0 4px rgba(255, 107, 107, 0.3) !important;
    }
    
    [data-theme="dark"] [data-testid="stAudioInput"] button:not(:disabled):hover {
        box-shadow: 0 0 8px rgba(255, 107, 107, 0.5) !important;
    }
    
    /* Make download and clear buttons visible */
    [data-testid="stAudioInput"] a,
    [data-testid="stAudioInput"] button[aria-label*="download"],
    [data-testid="stAudioInput"] button[aria-label*="clear"],
    [data-testid="stAudioInput"] a[download] {
        opacity: 1 !important;
        visibility: visible !important;
        display: inline-block !important;
        background-color: var(--button-primary) !important;
        color: white !important;
        padding: 8px 16px !important;
        border-radius: 5px !important;
        margin: 5px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        text-decoration: none !important;
        border: none !important;
        cursor: pointer !important;
    }
    
    [data-testid="stAudioInput"] a:hover,
    [data-testid="stAudioInput"] button[aria-label*="download"]:hover,
    [data-testid="stAudioInput"] button[aria-label*="clear"]:hover {
        background-color: var(--button-primary-hover) !important;
        opacity: 1 !important;
    }
    
    /* Style the audio player controls */
    [data-testid="stAudioInput"] audio {
        width: 100% !important;
        margin: 10px 0 !important;
    }
    
    /* Make the entire audio input container more visible */
    [data-testid="stAudioInput"] {
        padding: 10px !important;
        background-color: var(--mic-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 5px !important;
        margin: 10px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Check authentication
user = get_current_user()
if not user or not user.user:
    st.warning("Please log in to access the app.")
    st.switch_page("pages/4_Login.py")
    st.stop()

user_id = user.user.id
user_email = user.user.email

# Initialize session state
if 'current_view' not in st.session_state:
    st.session_state.current_view = "today"
if 'last_input' not in st.session_state:
    st.session_state.last_input = None

# Detect user timezone from browser - NEVER DEFAULT TO UTC
# ABSOLUTE RULE: If user location is known (NY/NJ), use America/New_York
# Only use UTC as absolute last resort, and FAIL LOUDLY

if 'user_timezone' not in st.session_state:
    # Try to get timezone from query params (set by JavaScript)
    timezone_param = st.query_params.get("tz", None)
    if timezone_param:
        st.session_state.user_timezone = timezone_param
        # Clear the query param to avoid reload loop
        st.query_params.clear()
    else:
        # Try to detect from system timezone
        detected_tz = None
        try:
            import time
            tz_name = time.tzname[0] if time.daylight == 0 else time.tzname[1]
            # Map to pytz timezone
            tz_mapping = {
                'PST': 'America/Los_Angeles',
                'PDT': 'America/Los_Angeles',
                'EST': 'America/New_York',
                'EDT': 'America/New_York',
                'CST': 'America/Chicago',
                'CDT': 'America/Chicago',
                'MST': 'America/Denver',
                'MDT': 'America/Denver',
            }
            detected_tz = tz_mapping.get(tz_name, None)
        except:
            pass
        
        # If we couldn't detect, use America/New_York as default (user is in NY/NJ)
        # NEVER silently default to UTC
        if not detected_tz:
            detected_tz = 'America/New_York'  # Default for NY/NJ users
            st.warning("⚠️ Could not detect timezone from browser. Using America/New_York as default. Please refresh the page to detect your timezone.")
        
        st.session_state.user_timezone = detected_tz

# Get user timezone - NEVER allow UTC unless explicitly set
user_tz = st.session_state.get('user_timezone', 'America/New_York')

# GUARDRAIL: Fail loudly if timezone is UTC unexpectedly
if user_tz == 'UTC':
    st.error("🚨 CRITICAL ERROR: User timezone is UTC! This should never happen. Using America/New_York as fallback.")
    user_tz = 'America/New_York'
    st.session_state.user_timezone = 'America/New_York'

# Show detected timezone for debugging (temporary - remove after fixing)
with st.expander("🔍 Debug: Timezone Info", expanded=False):
    st.write(f"**Detected timezone:** {user_tz}")
    from datetime import datetime
    import pytz
    tz = pytz.timezone(user_tz)
    current_time = datetime.now(tz)
    st.write(f"**Current time in your timezone:** {current_time.strftime('%I:%M %p %Z')}")
    st.write(f"**Current time UTC:** {datetime.utcnow().strftime('%I:%M %p UTC')}")

# Add JavaScript to detect and send timezone to Streamlit (only if not already set)
# This runs on every page load until timezone is detected
if 'user_timezone' not in st.session_state or st.session_state.get('user_timezone') == 'UTC':
    st.markdown("""
    <script>
        // Detect timezone and send to Streamlit via query params
        (function() {
            try {
                const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                console.log('🌍 Detected browser timezone:', timezone);
                
                // Validate timezone is not UTC
                if (timezone === 'UTC') {
                    console.warn('⚠️ Browser timezone is UTC - this is unusual. Using America/New_York as fallback.');
                    // Don't set UTC - let Python code handle fallback
                    return;
                }
                
                const currentUrl = new URL(window.location);
                const existingTz = currentUrl.searchParams.get('tz');
                
                // Only update if timezone changed or not set
                if (!existingTz || existingTz !== timezone) {
                    currentUrl.searchParams.set('tz', timezone);
                    window.history.replaceState({}, '', currentUrl);
                    console.log('✅ Timezone set in URL:', timezone);
                    
                    // Trigger a rerun to update session state
                    setTimeout(() => {
                        window.location.reload();
                    }, 50);
                }
            } catch (e) {
                console.error('❌ Error detecting timezone:', e);
            }
        })();
    </script>
    """, unsafe_allow_html=True)

# Main content area
# Header with title and logout button
header_col1, header_col2 = st.columns([5, 1])
with header_col1:
    st.title("Skkadoosh")
with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Align button with title
    if st.button("Logout", type="primary", use_container_width=True, key="logout_btn"):
        from database import sign_out
        sign_out()
        st.session_state.clear()
        st.switch_page("pages/1_Skkadoosh.py")

# Navigation header (tabs style below title)
nav_options = ["Today", "Week", "Upcoming", "Completed"]
nav_cols = st.columns(len(nav_options))

view_map = {
    "Today": "today",
    "Week": "week", 
    "Upcoming": "upcoming",
    "Completed": "completed"
}

# Create navigation buttons
for idx, nav_option in enumerate(nav_options):
    with nav_cols[idx]:
        # Style the button based on current view
        is_active = st.session_state.current_view == view_map[nav_option]
        button_type = "primary" if is_active else "secondary"
        
        if st.button(nav_option, key=f"nav_{nav_option}", use_container_width=True, type=button_type):
            st.session_state.current_view = view_map[nav_option]
            st.rerun()

# Get tasks
all_tasks = get_tasks(user_id)

# Display tasks based on current view (no header - navigation shows the view)
if st.session_state.current_view in ["today", "week", "upcoming"]:
    user_tz = st.session_state.get('user_timezone', 'UTC')
    view_tasks = filter_tasks_by_view(all_tasks, st.session_state.current_view, user_timezone=user_tz)
    
    if not view_tasks:
        st.info(f"No tasks for {st.session_state.current_view}. Add a task below!")
    else:
        for task in view_tasks:
            with st.container():
                priority = task.get("priority", "medium")
                priority_class = f"priority-{priority}"
                
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    description_html = f'<p style="color: var(--text-color); margin: 5px 0;">{task.get("description", "")}</p>' if task.get('description') else ''
                    due_date_str = task.get('due_date', '') if task.get('due_date') else 'No due date'
                    if due_date_str != 'No due date':
                        try:
                            # Parse the stored datetime (already in user's timezone with correct offset)
                            # Just parse and display - NO conversion needed
                            dt = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                            # Display in the timezone it was stored in (user's timezone)
                            # Get user timezone from session state or use stored timezone
                            if 'user_timezone' in st.session_state:
                                user_tz = pytz.timezone(st.session_state['user_timezone'])
                                # Convert to user's timezone for display (should be same, but ensures consistency)
                                if dt.tzinfo:
                                    dt = dt.astimezone(user_tz)
                                else:
                                    dt = user_tz.localize(dt)
                            due_date_str = dt.strftime("%b %d, %Y %I:%M %p")
                        except Exception as e:
                            # If parsing fails, show raw string
                            pass
                    
                    st.markdown(f"""
                    <div class="task-item {priority_class}">
                        <h4 style="margin: 0; color: var(--heading-color);">{task.get('title', 'Untitled')}</h4>
                        {description_html}
                        Priority: {priority.upper()} | Due: {due_date_str}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Task action buttons (center aligned)
                    action_cols = st.columns(4)
                    
                    with action_cols[0]:
                        if st.button("✓", key=f"done_{task['id']}", help="Mark done", use_container_width=True):
                            mark_task_complete(task['id'], user_id)
                            save_transcript(user_id, f"Marked task '{task.get('title')}' as done")
                            try:
                                send_task_update_email(user_email, user_id, "updated")
                            except:
                                pass
                            st.rerun()
                    
                    with action_cols[1]:
                        if st.button("✏️", key=f"edit_{task['id']}", help="Edit", use_container_width=True):
                            st.session_state[f"editing_{task['id']}"] = True
                            st.rerun()
                    
                    with action_cols[2]:
                        if st.button("⏰", key=f"snooze_{task['id']}", help="Snooze", use_container_width=True):
                            st.session_state[f"snoozing_{task['id']}"] = True
                            st.rerun()
                    
                    with action_cols[3]:
                        if st.button("🗑️", key=f"delete_{task['id']}", help="Delete", use_container_width=True):
                            delete_task(task['id'], user_id)
                            try:
                                send_task_update_email(user_email, user_id, "updated")
                            except:
                                pass
                            st.rerun()
                
                st.divider()
                
                # Edit box (moved below task section)
                if st.session_state.get(f"editing_{task['id']}"):
                    with st.container():
                        st.markdown(f"**Edit: {task.get('title')}**")
                        new_title = st.text_input("Title", value=task.get('title', ''), key=f"edit_title_{task['id']}")
                        new_desc = st.text_area("Description", value=task.get('description', ''), key=f"edit_desc_{task['id']}")
                        new_priority = st.selectbox("Priority", ["p0", "high", "medium", "low"], 
                                                   index=["p0", "high", "medium", "low"].index(task.get('priority', 'medium')),
                                                   key=f"edit_priority_{task['id']}")
                        # Date and time pickers for due date
                        col_date, col_time = st.columns(2)
                        with col_date:
                            # Parse existing due date if available
                            existing_date = None
                            existing_time = None
                            if task.get('due_date'):
                                try:
                                    # Parse stored datetime (already in user's timezone)
                                    dt = datetime.fromisoformat(task.get('due_date').replace('Z', '+00:00'))
                                    # Convert to user's current timezone for editing
                                    if 'user_timezone' in st.session_state:
                                        user_tz = pytz.timezone(st.session_state['user_timezone'])
                                        if dt.tzinfo:
                                            dt = dt.astimezone(user_tz)
                                        else:
                                            dt = user_tz.localize(dt)
                                    existing_date = dt.date()
                                    existing_time = dt.time()
                                except:
                                    pass
                            
                            new_due_date_obj = st.date_input("Due Date", value=existing_date if existing_date else datetime.now().date(), 
                                                             key=f"edit_date_{task['id']}", 
                                                             min_value=datetime.now().date())
                        with col_time:
                            new_due_time = st.time_input("Due Time", value=existing_time if existing_time else datetime.now().time(), 
                                                         key=f"edit_time_{task['id']}")
                        
                        # Combine date and time into ISO format
                        if new_due_date_obj and new_due_time:
                            local_tz = datetime.now().astimezone().tzinfo
                            new_due_date = datetime.combine(new_due_date_obj, new_due_time, local_tz).isoformat()
                        else:
                            new_due_date = None
                        
                        col_save, col_cancel = st.columns(2)
                        save_button_clicked = False
                        cancel_button_clicked = False
                        
                        save_button_clicked = False
                        cancel_button_clicked = False
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("Save", key=f"save_edit_{task['id']}"):
                                save_button_clicked = True
                        with col_cancel:
                            if st.button("Cancel", key=f"cancel_edit_{task['id']}"):
                                cancel_button_clicked = True
                        
                        # Process Save button - ONLY send email if Save was clicked, NOT Cancel
                        if save_button_clicked and not cancel_button_clicked:
                            # Save button clicked - update task and send email
                            updates = {"title": new_title, "description": new_desc, "priority": new_priority}
                            if new_due_date:
                                updates["due_date"] = new_due_date
                            else:
                                updates["due_date"] = None
                            update_task(task['id'], user_id, **updates)
                            st.session_state[f"editing_{task['id']}"] = False
                            # Send email ONLY when Save is explicitly clicked
                            try:
                                send_task_update_email(user_email, user_id, "updated")
                            except:
                                pass
                            st.rerun()
                        elif cancel_button_clicked:
                            # Cancel button clicked - do NOT update task, do NOT send email
                            st.session_state[f"editing_{task['id']}"] = False
                            st.rerun()
                        st.divider()
                
                # Snooze box (moved below task section)
                if st.session_state.get(f"snoozing_{task['id']}"):
                    with st.container():
                        st.markdown(f"**Snooze: {task.get('title')}**")
                        snooze_option = st.selectbox("Snooze until", 
                            ["5 min", "10 min", "15 min", "30 min", "1 hr", "2 hr", "Tomorrow 9am", "Next week", "Custom"],
                            key=f"snooze_option_{task['id']}")
                        
                        custom_date = None
                        custom_time = None
                        custom_ampm = "AM"
                        if snooze_option == "Custom":
                            col_date, col_time, col_ampm = st.columns(3)
                            with col_date:
                                custom_date = st.date_input("Date", key=f"custom_date_{task['id']}", min_value=datetime.now().date())
                            with col_time:
                                custom_time = st.time_input("Time", key=f"custom_time_{task['id']}")
                            
                            snooze_button_clicked = False
                            cancel_snooze_clicked = False
                            
                            col_snooze, col_cancel_snooze = st.columns(2)
                            with col_snooze:
                                if st.button("Snooze", key=f"confirm_snooze_{task['id']}"):
                                    snooze_button_clicked = True
                            with col_cancel_snooze:
                                if st.button("Cancel", key=f"cancel_snooze_{task['id']}"):
                                    cancel_snooze_clicked = True
                            
                            # Process Snooze button - ONLY send email if Snooze was clicked, NOT Cancel
                            if snooze_button_clicked and not cancel_snooze_clicked:
                                from datetime import timedelta
                                local_tz = datetime.now().astimezone().tzinfo
                                now = datetime.now(local_tz)
                                
                                if custom_date and custom_time:
                                    snooze_until = datetime.combine(custom_date, custom_time, local_tz).isoformat()
                                else:
                                    snooze_until = (now + timedelta(hours=2)).isoformat()
                                
                                snooze_task(task['id'], user_id, snooze_until)
                                st.session_state[f"snoozing_{task['id']}"] = False
                                # Send email ONLY when Snooze is explicitly clicked
                                try:
                                    send_task_update_email(user_email, user_id, "updated")
                                except:
                                    pass
                                st.rerun()
                            elif cancel_snooze_clicked:
                                # Cancel snooze - do NOT send email, just close snooze box
                                st.session_state[f"snoozing_{task['id']}"] = False
                                st.rerun()
                        else:
                            snooze_button_clicked = False
                            cancel_snooze_clicked = False
                            
                            col_snooze, col_cancel_snooze = st.columns(2)
                            with col_snooze:
                                if st.button("Snooze", key=f"confirm_snooze_{task['id']}"):
                                    snooze_button_clicked = True
                            with col_cancel_snooze:
                                if st.button("Cancel", key=f"cancel_snooze_{task['id']}"):
                                    cancel_snooze_clicked = True
                            
                            # Process Snooze button - ONLY send email if Snooze was clicked, NOT Cancel
                            if snooze_button_clicked and not cancel_snooze_clicked:
                                from datetime import timedelta
                                local_tz = datetime.now().astimezone().tzinfo
                                now = datetime.now(local_tz)
                                
                                if snooze_option == "5 min":
                                    snooze_until = (now + timedelta(minutes=5)).isoformat()
                                elif snooze_option == "10 min":
                                    snooze_until = (now + timedelta(minutes=10)).isoformat()
                                elif snooze_option == "15 min":
                                    snooze_until = (now + timedelta(minutes=15)).isoformat()
                                elif snooze_option == "30 min":
                                    snooze_until = (now + timedelta(minutes=30)).isoformat()
                                elif snooze_option == "1 hr":
                                    snooze_until = (now + timedelta(hours=1)).isoformat()
                                elif snooze_option == "2 hr":
                                    snooze_until = (now + timedelta(hours=2)).isoformat()
                                elif snooze_option == "Tomorrow 9am":
                                    tomorrow = now + timedelta(days=1)
                                    snooze_until = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0).isoformat()
                                elif snooze_option == "Next week":
                                    days_until_next_week = 7 - now.weekday()
                                    snooze_until = (now + timedelta(days=days_until_next_week)).isoformat()
                                
                                snooze_task(task['id'], user_id, snooze_until)
                                st.session_state[f"snoozing_{task['id']}"] = False
                                # Send email ONLY when Snooze is explicitly clicked
                                try:
                                    send_task_update_email(user_email, user_id, "updated")
                                except:
                                    pass
                                st.rerun()
                            elif cancel_snooze_clicked:
                                # Cancel snooze - do NOT send email, just close snooze box
                                st.session_state[f"snoozing_{task['id']}"] = False
                                st.rerun()
                        st.divider()

elif st.session_state.current_view == "completed":
    # Header removed - navigation shows selected view
    completed_tasks = [t for t in all_tasks if t.get("status") == "completed"]
    
    if not completed_tasks:
        st.info("No completed tasks yet.")
    else:
        grouped = group_tasks_by_date(completed_tasks)
        for date_key in sorted(grouped.keys(), reverse=True):
            st.subheader(date_key)
            for task in grouped[date_key]:
                st.markdown(f"- ~~{task.get('title', 'Untitled')}~~")
            st.divider()


# Input area at bottom (ChatGPT-style)
st.markdown("---")
st.markdown("### Add Task")

# Create input container with microphone icon (ChatGPT-style)
# Use columns to place microphone icon next to text input
input_col1, input_col2 = st.columns([11, 1])

with input_col1:
    # Text input (will be populated with transcription)
    # IMPORTANT: To make transcribed text appear in the widget, we need to set the widget's session state directly
    # Streamlit widgets with keys maintain their own state, so we set st.session_state["task_input"] directly
    
    # If we have transcribed text, set it directly in the widget's session state
    if 'transcribed_text' in st.session_state and st.session_state.transcribed_text:
        # Set the widget value directly in session state (this is the key to making it appear!)
        st.session_state["task_input"] = st.session_state.transcribed_text
    
    # Also check if we need to clear the field after task creation
    if 'clear_input' in st.session_state and st.session_state.clear_input:
        # Clear the widget value
        if "task_input" in st.session_state:
            st.session_state["task_input"] = ""
        del st.session_state.clear_input
        # Also clear transcribed text when clearing input
        if 'transcribed_text' in st.session_state:
            del st.session_state.transcribed_text
    
    # Create the text input widget - it will use the value from st.session_state["task_input"] if set
    user_input = st.text_input(
        "Type or speak your task...",
        key="task_input",
        placeholder="Message Skkadoosh...",
        label_visibility="collapsed"
    )

with input_col2:
    # Small microphone button - positioned next to text input, same height, custom background
    # Ensure the column doesn't block clicks
    st.markdown("""
    <style>
    [data-testid="column"]:has([data-testid="stAudioInput"]) {
        pointer-events: auto !important;
    }
    </style>
    """, unsafe_allow_html=True)
    audio_data = st.audio_input("🎤", label_visibility="collapsed", key="audio_recorder")

# Process audio if recorded (st.audio_input processes after recording completes)
# Use a flag to track if we've already processed this audio to avoid infinite loop
if audio_data is not None:
    # Check if we've already processed this audio (using audio_data size as identifier)
    try:
        audio_bytes = audio_data.read()
        audio_id = f"audio_{len(audio_bytes)}"
        audio_data.seek(0)  # Reset file pointer
    except:
        audio_id = "audio_0"
        audio_bytes = None
    
    if audio_bytes and ('last_processed_audio' not in st.session_state or st.session_state.last_processed_audio != audio_id):
        with st.spinner("Transcribing audio..."):
            try:
                # Transcribe using Gemini 2.5 Flash
                transcribed_text = transcribe_audio_bytes(audio_bytes, mime_type="audio/webm")
                
                if not transcribed_text or not transcribed_text.strip():
                    st.error("Transcription returned empty text. Please try recording again.")
                    st.session_state.last_processed_audio = audio_id
                else:
                    # Store transcribed text in a temporary session state key (don't show message, don't auto-process)
                    st.session_state.transcribed_text = transcribed_text
                    st.session_state.last_processed_audio = audio_id
                    st.rerun()
            except Exception as e:
                error_msg = str(e)
                # Show detailed error message
                st.error(f"❌ **Error transcribing audio:** {error_msg}")
                
                # Show full error details in expander for debugging
                with st.expander("🔍 Show detailed error information"):
                    import traceback
                    st.code(traceback.format_exc(), language="python")
                    st.write("**Error type:**", type(e).__name__)
                    st.write("**Error message:**", str(e))
                
                st.info("💡 **Tips:**\n- Make sure your microphone is working\n- Check your internet connection\n- Verify your Gemini API key is valid\n- Try recording again with clear audio")
                
                st.session_state.last_processed_audio = audio_id  # Mark as processed even on error to avoid loop

# Send button
if st.button("Send", type="primary", use_container_width=True, key="send_btn"):
    input_text = None
    
    # Check if user entered text in the widget
    if user_input and user_input.strip():
        input_text = user_input.strip()
    else:
        st.warning("Please enter some text in the text field before clicking Send.")
    
    if input_text:
        try:
            # Save transcript
            save_transcript(user_id, input_text)
            
            # Get incomplete tasks for context
            incomplete_tasks = [t for t in all_tasks if t.get("status") != "completed"]
            
            # Parse input with Gemini
            with st.spinner("Processing your input..."):
                try:
                    # Get user timezone - MUST be set and NOT UTC
                    user_tz = st.session_state.get('user_timezone', 'America/New_York')
                    if user_tz == 'UTC':
                        st.error("🚨 CRITICAL: User timezone is UTC! Using America/New_York as fallback.")
                        user_tz = 'America/New_York'
                        st.session_state.user_timezone = 'America/New_York'
                    
                    # user_timezone is now REQUIRED - no default
                    result = parse_user_input(input_text, incomplete_tasks, user_timezone=user_tz)
                    
                    # Process actions
                    action_type = result.get("action_type", "")
                    
                    if action_type == "clarification":
                        st.info(result.get("clarification_question", "Could you clarify?"))
                    else:
                        tasks_added = 0
                        # Add new tasks
                        tasks_to_add = result.get("tasks_to_add", [])
                        
                        if not tasks_to_add:
                            st.warning("No tasks to add. Gemini may not have detected a task in your input. Try being more explicit, e.g., 'Add task: Buy groceries'")
                        
                        for task_data in tasks_to_add:
                            try:
                                # Normalize dates to user's timezone
                                from gemini_integration import normalize_datetime_to_timezone
                                due_date = task_data.get("due_date")
                                reminder_time = task_data.get("reminder_time")
                                
                                # Debug: Show what Gemini returned and validate
                                if due_date:
                                    st.write(f"🔍 Debug: Gemini returned due_date: {due_date}")
                                    original_hour = None
                                    try:
                                        # Extract hour from Gemini's response for validation
                                        import re
                                        time_match = re.search(r'T(\d{2}):(\d{2})', due_date)
                                        if time_match:
                                            original_hour = int(time_match.group(1))
                                    except:
                                        pass
                                    
                                    due_date = normalize_datetime_to_timezone(due_date, user_tz)
                                    st.write(f"🔍 Debug: Normalized to {user_tz}: {due_date}")
                                    
                                    # Validate: hour should be preserved
                                    if original_hour is not None:
                                        try:
                                            normalized_hour = int(due_date.split('T')[1].split(':')[0])
                                            if normalized_hour != original_hour:
                                                st.warning(f"⚠️ WARNING: Hour changed from {original_hour} to {normalized_hour} - this should not happen!")
                                        except:
                                            pass
                                
                                if reminder_time:
                                    reminder_time = normalize_datetime_to_timezone(reminder_time, user_tz)
                                
                                create_task(
                                    user_id=user_id,
                                    title=task_data.get("title"),
                                    description=task_data.get("description", ""),
                                    due_date=due_date,
                                    priority=task_data.get("priority", "medium"),
                                    reminder_time=reminder_time
                                )
                                tasks_added += 1
                            except Exception as task_error:
                                st.error(f"Error creating task: {str(task_error)}")
                                import traceback
                                st.exception(task_error)
                        
                        if tasks_added == 0 and len(tasks_to_add) > 0:
                            st.warning("No tasks were created. Please try again.")
                        elif tasks_added > 0:
                            pass  # Success message shown below
                        
                        # Update tasks - handle both task IDs and task titles
                        for update_data in result.get("tasks_to_update", []):
                            task_id = update_data.get("task_id")
                            task_title_ref = update_data.get("task_title")  # In case Gemini returns title instead
                            
                            # If task_id is not a valid UUID, try to match by title
                            if task_id and task_id not in [str(t['id']) for t in incomplete_tasks]:
                                # Try to find task by title reference
                                if task_title_ref:
                                    from gemini_integration import match_task_id_by_reference
                                    matched_id = match_task_id_by_reference(task_title_ref, incomplete_tasks)
                                    if matched_id:
                                        task_id = matched_id
                            
                            if task_id and task_id in [str(t['id']) for t in incomplete_tasks]:
                                updates = {}
                                if update_data.get("title"):
                                    updates["title"] = update_data["title"]
                                if update_data.get("due_date"):
                                    updates["due_date"] = update_data["due_date"]
                                if update_data.get("priority"):
                                    updates["priority"] = update_data["priority"]
                                if update_data.get("status") == "snoozed" and update_data.get("snooze_until"):
                                    snooze_task(task_id, user_id, update_data["snooze_until"])
                                elif updates:
                                    update_task(task_id, user_id, **updates)
                        
                        # Complete tasks - handle both task IDs and task titles
                        task_ids_to_complete = result.get("tasks_to_complete", [])
                        for task_ref in task_ids_to_complete:
                            # If it's a UUID, use it directly
                            if task_ref in [str(t['id']) for t in incomplete_tasks]:
                                mark_task_complete(task_ref, user_id)
                            else:
                                # Try to match by title
                                from gemini_integration import match_task_id_by_reference
                                matched_id = match_task_id_by_reference(task_ref, incomplete_tasks)
                                if matched_id:
                                    mark_task_complete(matched_id, user_id)
                        
                        # Switch view if suggested
                        suggested_view = result.get("suggested_view", "today")
                        if suggested_view:
                            st.session_state.current_view = suggested_view
                        
                        # Send update email (don't fail if email fails)
                        try:
                            send_task_update_email(user_email, user_id, "updated")
                        except Exception:
                            pass  # Email failure is non-critical
                        
                        # Clear text input after processing
                        st.session_state.clear_input = True
                        # Clear transcribed text as well
                        if 'transcribed_text' in st.session_state:
                            del st.session_state.transcribed_text
                        
                        if tasks_added > 0:
                            st.success(f"Task(s) created successfully! ({tasks_added} task(s) added)")
                        else:
                            st.info("Input processed, but no new tasks were created.")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error processing input: {str(e)}")
        except Exception as e:
            st.error(f"Error saving transcript: {str(e)}")
