"""
Utility functions
"""
from datetime import datetime, timedelta
import pytz
from typing import List, Dict

TZ = pytz.timezone("America/Los_Angeles")

def get_today_start() -> datetime:
    """Get start of today in LA timezone"""
    now = datetime.now(TZ)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)

def get_week_end() -> datetime:
    """Get end of this week (Sunday) in LA timezone"""
    today = get_today_start()
    days_until_sunday = (6 - today.weekday()) % 7
    if days_until_sunday == 0:
        days_until_sunday = 7
    return today + timedelta(days=days_until_sunday)

def filter_tasks_by_view(tasks: List[Dict], view: str) -> List[Dict]:
    """Filter tasks based on view (today, week, upcoming)"""
    now = datetime.now(TZ)
    today_start = get_today_start()
    week_end = get_week_end()
    
    filtered = []
    
    for task in tasks:
        if task.get("status") in ["completed", "deleted"]:
            continue
        
        due_date_str = task.get("due_date")
        if not due_date_str:
            # Tasks without due dates go to "today" or "upcoming" based on view
            if view == "today" or view == "upcoming":
                filtered.append(task)
            continue
        
        try:
            # Parse due date
            if 'T' in due_date_str:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            else:
                due_date = datetime.fromisoformat(due_date_str).replace(tzinfo=TZ)
            
            # Convert to LA timezone if needed
            if due_date.tzinfo is None:
                due_date = TZ.localize(due_date)
            else:
                due_date = due_date.astimezone(TZ)
            
            due_date_only = due_date.date()
            today_date = today_start.date()
            week_end_date = week_end.date()
            
            if view == "today":
                if due_date_only <= today_date:
                    filtered.append(task)
            elif view == "week":
                if due_date_only <= week_end_date:
                    filtered.append(task)
            elif view == "upcoming":
                if due_date_only > week_end_date:
                    filtered.append(task)
                    
        except Exception as e:
            # If parsing fails, include in "today" view
            if view == "today":
                filtered.append(task)
    
    return filtered

def group_tasks_by_date(tasks: List[Dict]) -> Dict[str, List[Dict]]:
    """Group tasks by completion date"""
    grouped = {}
    
    for task in tasks:
        if task.get("status") != "completed":
            continue
        
        completed_at = task.get("completed_at")
        if not completed_at:
            date_key = "No date"
        else:
            try:
                dt = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                dt = dt.astimezone(TZ)
                date_key = dt.strftime("%B %d, %Y")
            except:
                date_key = "Unknown date"
        
        if date_key not in grouped:
            grouped[date_key] = []
        grouped[date_key].append(task)
    
    return grouped
