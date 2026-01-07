"""
Scheduler script for sending daily reminder emails
This should be run as a cron job or scheduled task daily
"""
import schedule
import time
from datetime import datetime
import pytz
from database import get_supabase_client, get_tasks
from email_service import send_daily_reminder_email
from supabase import Client

def send_daily_reminders():
    """Send daily reminder emails to all users"""
    supabase: Client = get_supabase_client()
    
    try:
        # Get all users (this requires admin access or a users table)
        # For now, we'll get users from auth.users via Supabase admin
        # In production, you might want to maintain a separate users table
        
        # Get all tasks and group by user
        # This is a simplified version - in production, you'd want to batch this
        # and handle it more efficiently
        
        # For demonstration, we'll assume we have a way to get all user emails
        # In practice, you might maintain a users table with email preferences
        
        tz = pytz.UTC  # Use UTC for scheduled tasks
        now = datetime.now(tz)
        
        # This would need to be adapted based on your actual user management
        # For now, this is a placeholder that shows the structure
        
        print(f"Daily reminder job run at {now.isoformat()}")
        print("Note: Actual user fetching and email sending would be implemented here")
        
    except Exception as e:
        print(f"Error sending daily reminders: {str(e)}")

# Schedule the job to run daily at 8 AM LA time
schedule.every().day.at("08:00").do(send_daily_reminders)

if __name__ == "__main__":
    print("Daily reminder scheduler started. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
