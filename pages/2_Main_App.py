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
    page_title="NeverMiss - Dashboard",
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
    
    h1, h2, h3, h4 {
        font-family: 'Libre Baskerville', serif;
        color: #5C4E3D;
    }
    
    body, .stTextInput>div>div>input {
        font-family: 'DM Sans', sans-serif;
        color: #454240;
    }
    
    .task-item {
        background-color: #FFFDFA;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #B88E23;
        border-radius: 5px;
    }
    
    .priority-p0 { border-left-color: #FF0000; }
    .priority-high { border-left-color: #FF6B6B; }
    .priority-medium { border-left-color: #B88E23; }
    .priority-low { border-left-color: #5C4E3D; }
    
    /* Navigation header styling */
    .stButton > button {
        font-weight: 500;
        border-radius: 5px;
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
    
    /* Audio input styling - make microphone button visible and clickable */
    [data-testid="stAudioInput"] {
        background-color: #FFFDFA !important;
    }
    [data-testid="stAudioInput"] > div {
        background-color: #FFFDFA !important;
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
        background-color: #FFFDFA !important;
    }
    [data-testid="stAudioInput"] button:not(:disabled):hover {
        opacity: 0.8 !important;
        background-color: #f5f5f5 !important;
    }
    [data-testid="stAudioInput"] button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
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

# Sidebar for logout only
with st.sidebar:
    
    st.markdown(f"### Welcome, {user_email.split('@')[0]}")
    
    if st.button("Logout", use_container_width=True, type="primary"):
        from database import sign_out
        sign_out()
        st.session_state.clear()
        st.switch_page("pages/1_NeverMiss.py")

# Main content area
st.title("NeverMiss")

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
    view_tasks = filter_tasks_by_view(all_tasks, st.session_state.current_view)
    
    if not view_tasks:
        st.info(f"No tasks for {st.session_state.current_view}. Add a task below!")
    else:
        for task in view_tasks:
            with st.container():
                priority = task.get("priority", "medium")
                priority_class = f"priority-{priority}"
                
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    description_html = f'<p style="color: #454240; margin: 5px 0;">{task.get("description", "")}</p>' if task.get('description') else ''
                    due_date_str = task.get('due_date', '') if task.get('due_date') else 'No due date'
                    if due_date_str != 'No due date':
                        try:
                            # Use local timezone (browser/client timezone)
                            dt = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                            # Convert to local timezone
                            local_tz = datetime.now().astimezone().tzinfo
                            dt = dt.astimezone(local_tz)
                            due_date_str = dt.strftime("%b %d, %Y %I:%M %p")
                        except:
                            pass
                    
                    st.markdown(f"""
                    <div class="task-item {priority_class}">
                        <h4 style="margin: 0; color: #5C4E3D;">{task.get('title', 'Untitled')}</h4>
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
                                    dt = datetime.fromisoformat(task.get('due_date').replace('Z', '+00:00'))
                                    local_tz = datetime.now().astimezone().tzinfo
                                    dt = dt.astimezone(local_tz)
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
                        with col_save:
                            if st.button("Save", key=f"save_edit_{task['id']}"):
                                updates = {"title": new_title, "description": new_desc, "priority": new_priority}
                                if new_due_date:
                                    updates["due_date"] = new_due_date
                                else:
                                    updates["due_date"] = None
                                update_task(task['id'], user_id, **updates)
                                st.session_state[f"editing_{task['id']}"] = False
                                try:
                                    send_task_update_email(user_email, user_id, "updated")
                                except:
                                    pass
                                st.rerun()
                        with col_cancel:
                            if st.button("Cancel", key=f"cancel_edit_{task['id']}"):
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
                            
                            col_snooze, col_cancel_snooze = st.columns(2)
                            with col_snooze:
                                if st.button("Snooze", key=f"confirm_snooze_{task['id']}"):
                                    from datetime import timedelta
                                    local_tz = datetime.now().astimezone().tzinfo
                                    now = datetime.now(local_tz)
                                    
                                    if custom_date and custom_time:
                                        snooze_until = datetime.combine(custom_date, custom_time, local_tz).isoformat()
                                    else:
                                        snooze_until = (now + timedelta(hours=2)).isoformat()
                                    
                                    snooze_task(task['id'], user_id, snooze_until)
                                    st.session_state[f"snoozing_{task['id']}"] = False
                                    try:
                                        send_task_update_email(user_email, user_id, "updated")
                                    except:
                                        pass
                                    st.rerun()
                            with col_cancel_snooze:
                                if st.button("Cancel", key=f"cancel_snooze_{task['id']}"):
                                    st.session_state[f"snoozing_{task['id']}"] = False
                                    st.rerun()
                        else:
                            col_snooze, col_cancel_snooze = st.columns(2)
                            with col_snooze:
                                if st.button("Snooze", key=f"confirm_snooze_{task['id']}"):
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
                                    try:
                                        send_task_update_email(user_email, user_id, "updated")
                                    except:
                                        pass
                                    st.rerun()
                            with col_cancel_snooze:
                                if st.button("Cancel", key=f"cancel_snooze_{task['id']}"):
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
        st.write(f"DEBUG AUDIO: Set st.session_state['task_input'] = '{st.session_state.transcribed_text}'")
    
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
        placeholder="Message NeverMiss...",
        label_visibility="collapsed"
    )
    
    # Debug: Verify the widget has the transcribed text
    if user_input and 'transcribed_text' in st.session_state:
        if user_input == st.session_state.transcribed_text:
            st.write(f"DEBUG AUDIO: ✓ Text field successfully populated with transcribed text: '{user_input}'")
        else:
            st.write(f"DEBUG AUDIO: Widget has different text than transcribed_text")

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
                st.write(f"DEBUG AUDIO: Audio bytes length = {len(audio_bytes)}")
                st.write(f"DEBUG AUDIO: Audio ID = {audio_id}")
                
                # Transcribe using Gemini 2.5 Flash
                transcribed_text = transcribe_audio_bytes(audio_bytes, mime_type="audio/webm")
                
                st.write(f"DEBUG AUDIO: Transcription result = '{transcribed_text}'")
                st.write(f"DEBUG AUDIO: Transcription length = {len(transcribed_text) if transcribed_text else 0}")
                
                # Debug: Check if transcription succeeded
                if not transcribed_text or not transcribed_text.strip():
                    st.error("Transcription returned empty text. Please try recording again.")
                    st.session_state.last_processed_audio = audio_id
                else:
                    # Store transcribed text in a temporary session state key (don't show message, don't auto-process)
                    st.write(f"DEBUG AUDIO: Storing transcribed text in session state")
                    st.session_state.transcribed_text = transcribed_text
                    st.session_state.last_processed_audio = audio_id
                    st.write(f"DEBUG AUDIO: Triggering rerun to populate text field")
                    st.rerun()
            except Exception as e:
                st.error(f"Error transcribing audio: {str(e)}")
                import traceback
                st.write(f"DEBUG AUDIO: Full error traceback:")
                st.code(traceback.format_exc())
                st.session_state.last_processed_audio = audio_id  # Mark as processed even on error to avoid loop

# Send button
if st.button("Send", type="primary", use_container_width=True, key="send_btn"):
    input_text = None
    
    # Debug: Check what we received
    st.write(f"DEBUG: user_input = '{user_input}'")
    st.write(f"DEBUG: user_input type = {type(user_input)}")
    
    # Check if user entered text in the widget
    if user_input and user_input.strip():
        input_text = user_input.strip()
        st.write(f"DEBUG: input_text = '{input_text}'")
    else:
        st.warning("Please enter some text in the text field before clicking Send.")
    
    if input_text:
        try:
            # Save transcript
            save_transcript(user_id, input_text)
            st.write(f"DEBUG: Transcript saved")
            
            # Get incomplete tasks for context
            incomplete_tasks = [t for t in all_tasks if t.get("status") != "completed"]
            st.write(f"DEBUG: Found {len(incomplete_tasks)} incomplete tasks")
            
            # Parse input with Gemini
            with st.spinner("Processing your input..."):
                try:
                    result = parse_user_input(input_text, incomplete_tasks)
                    st.write(f"DEBUG: parse_user_input result = {result}")
                    
                    # Process actions
                    action_type = result.get("action_type", "")
                    st.write(f"DEBUG: action_type = '{action_type}'")
                    
                    if action_type == "clarification":
                        st.info(result.get("clarification_question", "Could you clarify?"))
                    else:
                        tasks_added = 0
                        # Add new tasks
                        tasks_to_add = result.get("tasks_to_add", [])
                        st.write(f"DEBUG: tasks_to_add = {tasks_to_add}")
                        st.write(f"DEBUG: tasks_to_add length = {len(tasks_to_add)}")
                        
                        if not tasks_to_add:
                            st.warning("No tasks to add. Gemini may not have detected a task in your input. Try being more explicit, e.g., 'Add task: Buy groceries'")
                        
                        for task_data in tasks_to_add:
                            try:
                                st.write(f"DEBUG: Creating task: {task_data}")
                                create_task(
                                    user_id=user_id,
                                    title=task_data.get("title"),
                                    description=task_data.get("description", ""),
                                    due_date=task_data.get("due_date"),
                                    priority=task_data.get("priority", "medium"),
                                    reminder_time=task_data.get("reminder_time")
                                )
                                tasks_added += 1
                                st.write(f"DEBUG: Task created successfully")
                            except Exception as task_error:
                                st.error(f"Error creating task: {str(task_error)}")
                                st.write(f"DEBUG: Task creation error details: {task_error}")
                        
                        if tasks_added == 0 and len(tasks_to_add) > 0:
                            st.warning("No tasks were created. Check the debug output above for errors.")
                        elif tasks_added > 0:
                            st.write(f"DEBUG: Successfully created {tasks_added} task(s)")
                        
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
                        except Exception as email_error:
                            st.write(f"DEBUG: Email send failed (non-critical): {email_error}")
                        
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
                    import traceback
                    st.write(f"DEBUG: Full error traceback:")
                    st.code(traceback.format_exc())
        except Exception as e:
            st.error(f"Error saving transcript: {str(e)}")
            import traceback
            st.write(f"DEBUG: Transcript save error traceback:")
            st.code(traceback.format_exc())
