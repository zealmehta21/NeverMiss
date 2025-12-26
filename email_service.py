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
    """Format a single task as HTML"""
    priority_colors = {
        "p0": "#FF0000",
        "high": "#FF6B6B",
        "medium": "#B88E23",
        "low": "#5C4E3D"
    }
    priority = task.get("priority", "medium")
    color = priority_colors.get(priority, "#5C4E3D")
    
    due_date = task.get("due_date", "")
    if due_date:
        try:
            dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            due_str = dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            due_str = due_date
    else:
        due_str = "No due date"
    
    status = task.get("status", "pending")
    status_badge = "✓" if status == "completed" else "○"
    
    html = f"""
    <div style="margin: 10px 0; padding: 10px; border-left: 4px solid {color}; background-color: #FFFDFA;">
        <div style="font-weight: bold; color: #5C4E3D;">{status_badge} {task.get('title', 'Untitled')}</div>
        {f'<div style="color: #454240; font-size: 0.9em; margin-top: 5px;">{task.get("description", "")}</div>' if task.get("description") else ''}
        <div style="color: #454240; font-size: 0.85em; margin-top: 5px;">
            Due: {due_str} | Priority: {priority.upper()}
        </div>
    </div>
    """
    return html

def send_daily_reminder_email(user_email: str, user_id: str):
    """Send daily task reminder email"""
    tz = pytz.timezone("America/Los_Angeles")
    today = datetime.now(tz).date()
    
    # Get today's tasks
    all_tasks = get_tasks(user_id)
    today_tasks = [t for t in all_tasks if t.get("status") != "completed"]
    
    # Filter tasks for today (or overdue)
    today_tasks_filtered = []
    for task in today_tasks:
        due_date = task.get("due_date")
        if due_date:
            try:
                task_date = datetime.fromisoformat(due_date.replace('Z', '+00:00')).date()
                if task_date <= today:
                    today_tasks_filtered.append(task)
            except:
                pass
        else:
            # Include tasks without due dates
            today_tasks_filtered.append(task)
    
    subject = f"NeverMiss - Your Daily Task List - {today.strftime('%B %d, %Y')}"
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'DM Sans', sans-serif; color: #454240; background-color: #FFFDFA; }}
            h1 {{ font-family: 'Libre Baskerville', serif; color: #5C4E3D; }}
        </style>
    </head>
    <body>
        <h1>Your Daily Task List</h1>
        <p>Here are your tasks for {today.strftime('%B %d, %Y')}:</p>
        <div>
            {''.join([format_task_html(task) for task in today_tasks_filtered[:20]])}
        </div>
        <p style="margin-top: 20px; color: #454240;">
            <a href="https://your-app-url.com" style="color: #B88E23;">View in NeverMiss →</a>
        </p>
    </body>
    </html>
    """
    
    return send_email(user_email, subject, html_body)

def send_task_update_email(user_email: str, user_id: str, change_type: str = "updated"):
    """Send email when tasks are updated"""
    all_tasks = get_tasks(user_id)
    active_tasks = [t for t in all_tasks if t.get("status") != "completed"]
    
    subject = f"NeverMiss - Your Task List Has Been {change_type.capitalize()}"
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'DM Sans', sans-serif; color: #454240; background-color: #FFFDFA; }}
            h1 {{ font-family: 'Libre Baskerville', serif; color: #5C4E3D; }}
        </style>
    </head>
    <body>
        <h1>Your Task List Has Been {change_type.capitalize()}</h1>
        <p>Here's your updated task list:</p>
        <div>
            {''.join([format_task_html(task) for task in active_tasks[:20]])}
        </div>
        <p style="margin-top: 20px; color: #454240;">
            <a href="https://your-app-url.com" style="color: #B88E23;">View in NeverMiss →</a>
        </p>
    </body>
    </html>
    """
    
    return send_email(user_email, subject, html_body)
