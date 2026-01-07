"""
Database utilities for Supabase
Uses Supabase Auth for authentication
"""
from supabase import create_client, Client
import streamlit as st
from config import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime
from typing import List, Dict, Optional
import pytz

# Initialize anonymous Supabase client (for auth operations)
@st.cache_resource
def get_supabase_client() -> Client:
    """Get anonymous Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and KEY must be set in environment variables")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Get authenticated Supabase client (for DB operations with RLS)
def get_authenticated_client() -> Client:
    """Get authenticated Supabase client with access token"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and KEY must be set in environment variables")
    
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Apply the JWT token for authenticated requests (this enables RLS)
    if "sb_access_token" in st.session_state and st.session_state["sb_access_token"]:
        # Set the auth header for postgrest requests
        client.postgrest.auth(st.session_state["sb_access_token"])
    
    return client

# Authentication functions
def sign_up(email: str, password: str) -> Dict:
    """Sign up a new user using Supabase Auth"""
    supabase = get_supabase_client()
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        # If session is returned (no email confirmation required)
        if response.session:
            # Store session tokens
            st.session_state["sb_access_token"] = response.session.access_token
            st.session_state["sb_refresh_token"] = response.session.refresh_token
            st.session_state["sb_user"] = {
                "id": response.user.id,
                "email": response.user.email
            }
            
            return {
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                },
                "session": response.session
            }
        else:
            # Email confirmation required
            return {
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                },
                "session": None,
                "requires_confirmation": True
            }
    except Exception as e:
        raise Exception(f"Error creating user: {str(e)}")

def sign_in(email: str, password: str) -> Dict:
    """Sign in user using Supabase Auth"""
    supabase = get_supabase_client()
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.session and response.user:
            # Store session tokens
            st.session_state["sb_access_token"] = response.session.access_token
            st.session_state["sb_refresh_token"] = response.session.refresh_token
            st.session_state["sb_user"] = {
                "id": response.user.id,
                "email": response.user.email
            }
            
            return {
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                },
                "session": response.session
            }
        else:
            raise Exception("Failed to sign in - no session returned")
    except Exception as e:
        raise Exception(f"Error signing in: {str(e)}")

def sign_out():
    """Sign out current user"""
    supabase = get_supabase_client()
    try:
        # Clear Supabase session
        if "sb_access_token" in st.session_state:
            supabase.auth.sign_out()
    except:
        pass  # Ignore errors during sign out
    
    # Clear session state
    if "sb_access_token" in st.session_state:
        del st.session_state["sb_access_token"]
    if "sb_refresh_token" in st.session_state:
        del st.session_state["sb_refresh_token"]
    if "sb_user" in st.session_state:
        del st.session_state["sb_user"]
    if "user" in st.session_state:
        del st.session_state["user"]
    
    st.session_state.clear()

def get_current_user():
    """Get current authenticated user from session state"""
    if "sb_user" in st.session_state and st.session_state["sb_user"]:
        # Return in format compatible with existing code
        class UserWrapper:
            def __init__(self, user_data):
                self.user = type('User', (), user_data)()
        
        return UserWrapper(st.session_state["sb_user"])
    return None

def get_user_id() -> Optional[str]:
    """Get current user ID from session state"""
    if "sb_user" in st.session_state and st.session_state["sb_user"]:
        return st.session_state["sb_user"]["id"]
    return None

def reset_password_for_email(email: str):
    """Request password reset email using Supabase Auth"""
    supabase = get_supabase_client()
    try:
        # For local dev, you may need to set redirect URL in Supabase dashboard
        supabase.auth.reset_password_for_email(email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise Exception(f"Error sending password reset email: {str(e)}")

# Task operations
def create_task(user_id: str, title: str, description: str = "", 
                due_date: Optional[str] = None, priority: str = "medium",
                reminder_time: Optional[str] = None, status: str = "pending") -> Dict:
    """Create a new task (user_id parameter kept for compatibility, but RLS handles user isolation)"""
    supabase = get_authenticated_client()
    task_data = {
        "title": title,
        "description": description,
        "due_date": due_date,
        "priority": priority,  # low, medium, high, p0
        "reminder_time": reminder_time,
        "status": status,  # pending, completed, snoozed
        "created_at": datetime.now(pytz.UTC).isoformat(),
        "completed_at": None
    }
    
    try:
        result = supabase.table("tasks").insert(task_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Error creating task: {str(e)}")

def get_tasks(user_id: str, status: Optional[str] = None) -> List[Dict]:
    """Get tasks for user (user_id parameter kept for compatibility, but RLS ensures only user's tasks are returned)"""
    supabase = get_authenticated_client()
    query = supabase.table("tasks").select("*")
    
    if status:
        query = query.eq("status", status)
    else:
        query = query.neq("status", "deleted")
    
    try:
        result = query.order("created_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        raise Exception(f"Error fetching tasks: {str(e)}")

def update_task(task_id: str, user_id: str, **updates) -> Dict:
    """Update a task (user_id parameter kept for compatibility, but RLS ensures only user's tasks can be updated)"""
    supabase = get_authenticated_client()
    # Add updated_at timestamp
    updates["updated_at"] = datetime.now(pytz.UTC).isoformat()
    
    try:
        result = supabase.table("tasks").update(updates).eq("id", task_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Error updating task: {str(e)}")

def delete_task(task_id: str, user_id: str):
    """Soft delete a task (user_id parameter kept for compatibility, but RLS ensures only user's tasks can be deleted)"""
    return update_task(task_id, user_id, status="deleted")

def mark_task_complete(task_id: str, user_id: str):
    """Mark task as complete (user_id parameter kept for compatibility, but RLS ensures only user's tasks can be updated)"""
    return update_task(task_id, user_id, 
                      status="completed",
                      completed_at=datetime.now(pytz.UTC).isoformat())

def snooze_task(task_id: str, user_id: str, snooze_until: str):
    """Snooze a task until specified time (user_id parameter kept for compatibility, but RLS ensures only user's tasks can be updated)"""
    return update_task(task_id, user_id, 
                      status="snoozed",
                      snooze_until=snooze_until)

# Transcript operations
def save_transcript(user_id: str, transcript_text: str) -> Dict:
    """Save user transcript (user_id parameter kept for compatibility, but RLS handles user isolation)"""
    supabase = get_authenticated_client()
    transcript_data = {
        "transcript_text": transcript_text,
        "created_at": datetime.now(pytz.UTC).isoformat()
    }
    
    try:
        result = supabase.table("transcripts").insert(transcript_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Error saving transcript: {str(e)}")

def get_transcripts(user_id: str, limit: int = 50) -> List[Dict]:
    """Get recent transcripts for user (user_id parameter kept for compatibility, but RLS ensures only user's transcripts are returned)"""
    supabase = get_authenticated_client()
    try:
        result = supabase.table("transcripts").select("*").order("created_at", desc=True).limit(limit).execute()
        return result.data if result.data else []
    except Exception as e:
        raise Exception(f"Error fetching transcripts: {str(e)}")
