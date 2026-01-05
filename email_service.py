"""
Email service for sending task reminders and updates
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz
from typing import List, Dict
from config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD
from database import get_tasks, get_user_id
import streamlit as st

def send_email(to_email: str, subject: str, html_body: str):
    """Send email using SMTP"""
    if not all([SMTP_SERVER, SMTP_EMAIL, SMTP_PASSWORD]):
        st.warning("Email configuration not set. Skipping email send.")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        
        # Create plain text version
        text_body = html_body  # Simple fallback
        
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")
        return False

def format_task_html(task: Dict) -> str:
    """Format a single task as HTML - matches app display format exactly"""
    priority_colors = {
        "p0": "#FF0000",
        "high": "#FF6B6B",
        "medium": "#ff4b4b",
        "low": "#FFB3BA"
    }
    priority = task.get("priority", "medium")
    color = priority_colors.get(priority, "#ff4b4b")
    
    # Format due date exactly like the app does
    due_date_str = task.get('due_date', '') if task.get('due_date') else 'No due date'
    if due_date_str != 'No due date':
        try:
            # Parse ISO format date
            dt = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            # Convert to local timezone (same as app display)
            local_tz = datetime.now().astimezone().tzinfo
            dt = dt.astimezone(local_tz)
            # Use same format as app: "%b %d, %Y %I:%M %p"
            due_date_str = dt.strftime("%b %d, %Y %I:%M %p")
        except Exception as e:
            # If parsing fails, keep original
            pass
    
    status = task.get("status", "pending")
    status_badge = "✓" if status == "completed" else "○"
    
    html = f"""
    <div style="margin: 10px 0; padding: 10px; border-left: 4px solid {color}; background-color: #ffffff;">
        <div style="font-weight: bold; color: #333333;">{status_badge} {task.get('title', 'Untitled')}</div>
        {f'<div style="color: #454240; font-size: 0.9em; margin-top: 5px;">{task.get("description", "")}</div>' if task.get("description") else ''}
        <div style="color: #454240; font-size: 0.85em; margin-top: 5px;">
            Priority: {priority.upper()} | Due: {due_date_str}
        </div>
    </div>
    """
    return html

def send_daily_reminder_email(user_email: str, user_id: str):
    """Send daily task reminder email with accurate dates"""
    # Use local timezone for today's date
    local_tz = datetime.now().astimezone().tzinfo
    today = datetime.now(local_tz).date()
    
    # Get all active tasks
    all_tasks = get_tasks(user_id)
    active_tasks = [t for t in all_tasks if t.get("status") not in ["completed", "deleted"]]
    
    # Filter tasks for today (or overdue) - convert to local timezone for comparison
    today_tasks_filtered = []
    for task in active_tasks:
        due_date = task.get("due_date")
        if due_date:
            try:
                # Parse and convert to local timezone
                dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                dt = dt.astimezone(local_tz)
                task_date = dt.date()
                if task_date <= today:
                    today_tasks_filtered.append(task)
            except:
                # If parsing fails, include the task
                today_tasks_filtered.append(task)
        else:
            # Include tasks without due dates
            today_tasks_filtered.append(task)
    
    # Sort by due date
    def sort_key(task):
        due_date = task.get("due_date")
        if not due_date:
            return datetime.max
        try:
            dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            return dt
        except:
            return datetime.max
    
    today_tasks_filtered.sort(key=sort_key)
    
    subject = f"Skkadoosh - Your Daily Task List - {today.strftime('%B %d, %Y')}"
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'DM Sans', sans-serif; color: #454240; background-color: #ffffff; }}
            h1 {{ font-family: 'Libre Baskerville', serif; color: #333333; }}
        </style>
    </head>
    <body>
        <h1>Your Daily Task List</h1>
        <p>Here are your tasks for {today.strftime('%B %d, %Y')}:</p>
        <div>
            {''.join([format_task_html(task) for task in today_tasks_filtered])}
        </div>
        <p style="margin-top: 20px; color: #454240;">
            <a href="https://skkadoosh.com/NeverMiss" style="color: #ff4b4b;">View in Skkadoosh →</a>
        </p>
    </body>
    </html>
    """
    
    return send_email(user_email, subject, html_body)

def send_task_update_email(user_email: str, user_id: str, change_type: str = "updated"):
    """Send email when tasks are updated - includes all active tasks with accurate dates"""
    all_tasks = get_tasks(user_id)
    # Get all active tasks (not completed, not deleted) - same as app displays
    active_tasks = [t for t in all_tasks if t.get("status") not in ["completed", "deleted"]]
    
    # Sort tasks by due date (tasks without due dates go to end)
    def sort_key(task):
        due_date = task.get("due_date")
        if not due_date:
            return datetime.max
        try:
            dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            return dt
        except:
            return datetime.max
    
    active_tasks.sort(key=sort_key)
    
    subject = f"Skkadoosh - Your Task List Has Been {change_type.capitalize()}"
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'DM Sans', sans-serif; color: #454240; background-color: #ffffff; }}
            h1 {{ font-family: 'Libre Baskerville', serif; color: #333333; }}
        </style>
    </head>
    <body>
        <h1>Your Task List Has Been {change_type.capitalize()}</h1>
        <p>Here's your complete updated task list:</p>
        <div>
            {''.join([format_task_html(task) for task in active_tasks])}
        </div>
        <p style="margin-top: 20px; color: #454240;">
            <a href="https://skkadoosh.com/NeverMiss" style="color: #ff4b4b;">View in Skkadoosh →</a>
        </p>
    </body>
    </html>
    """
    
    return send_email(user_email, subject, html_body)
