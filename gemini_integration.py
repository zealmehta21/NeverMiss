"""
Gemini 3.0 integration for task parsing and voice command understanding
"""
from google import genai
import json
from datetime import datetime
import pytz
from typing import Dict, List, Optional
from config import GEMINI_API_KEY

# Configure Gemini
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not configured")
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are a task management assistant for Skkadoosh. Your role is to understand user input (text or transcribed voice) and extract actionable tasks, parse voice commands, and organize tasks intelligently.

You must output valid JSON only - no markdown, no explanations, just pure JSON.

Key capabilities:
1. Extract tasks from natural language
2. Parse voice commands (mark done, snooze, edit, change priority, set reminders)
3. Match spoken references to existing tasks using fuzzy matching
4. Determine appropriate due dates and priorities
5. Deduplicate similar tasks
6. Ask clarification questions only when confidence is very low

Always consider the current date and time when interpreting relative dates like "today", "tomorrow", "next week".
"""

PLANNER_PROMPT_TEMPLATE = """Given the user input and their current task list, determine what actions to take.

Current DateTime: {current_datetime}
Timezone: America/Los_Angeles

User Input: "{user_input}"

Existing Incomplete Tasks:
{existing_tasks}

Output JSON with this structure:
{{
    "action_type": "add_tasks" | "update_task" | "complete_task" | "mixed" | "clarification",
    "tasks_to_add": [
        {{
            "title": "task title",
            "description": "optional description",
            "due_date": "ISO 8601 datetime or null",
            "priority": "p0" | "high" | "medium" | "low",
            "reminder_time": "ISO 8601 datetime or null"
        }}
    ],
    "tasks_to_update": [
        {{
            "task_id": "id of existing task (use fuzzy matching)",
            "title": "new title or null",
            "due_date": "new ISO 8601 datetime or null",
            "priority": "new priority or null",
            "status": "snoozed" | null,
            "snooze_until": "ISO 8601 datetime or null",
            "reminder_time": "ISO 8601 datetime or null"
        }}
    ],
    "tasks_to_complete": ["task_id1", "task_id2"],
    "clarification_question": "question text or null",
    "suggested_view": "today" | "week" | "upcoming"
}}

Rules:
- CRITICAL: Only update existing tasks if the user EXPLICITLY mentions updating/changing/modifying/editing. Keywords: "update", "change", "modify", "edit", "move", "reschedule", "change the date of", "update my task", etc.
- If user just says "Buy X" or "Do X" or "X today", ALWAYS create a NEW task, even if a similar task exists. Users may need to do the same thing multiple times.
- If user says "X is done" or "I finished X", set action_type to "complete_task" and add X to tasks_to_complete
- If user says "snooze X for 2 hours" or "snooze X until tomorrow 9am", set status to "snoozed" and set snooze_until
- If user says "move X to Friday 3pm" or "reschedule X to Friday", update due_date (this is an explicit update command)
- If user says "make X P0" or "change priority of X", update priority (this is an explicit update command)
- If user says "remind me tomorrow at 11am to do X", add reminder_time
- Match tasks by title similarity (fuzzy match) ONLY when user explicitly mentions updating a specific task
- Only ask clarification if you're less than 70% confident about which task they mean
- DO NOT deduplicate automatically - always create new tasks unless user explicitly asks to update
- Parse natural language dates relative to current datetime
- When in doubt, CREATE a new task rather than updating an existing one
"""

COMMAND_PARSER_PROMPT_TEMPLATE = """Parse this voice command and identify the action:

Command: "{command}"
Existing Tasks: {existing_tasks}
Current DateTime: {current_datetime}

Output JSON:
{{
    "command_type": "mark_done" | "snooze" | "edit_date" | "change_priority" | "add_reminder" | "unknown",
    "target_task_ids": ["task_id1"],
    "parameters": {{
        "snooze_until": "ISO 8601 or null",
        "new_due_date": "ISO 8601 or null",
        "new_priority": "p0|high|medium|low or null",
        "reminder_time": "ISO 8601 or null"
    }},
    "confidence": 0.0-1.0,
    "clarification_needed": true|false,
    "clarification_question": "question or null"
}}
"""

def get_current_datetime_str() -> str:
    """Get current datetime string in LA timezone"""
    tz = pytz.timezone("America/Los_Angeles")
    return datetime.now(tz).isoformat()

def format_existing_tasks_for_prompt(tasks: List[Dict]) -> str:
    """Format existing tasks for Gemini prompt"""
    if not tasks:
        return "No existing tasks"
    
    formatted = []
    for task in tasks:
        task_id = task.get('id', '')
        task_title = task.get('title', 'Untitled')
        task_due = task.get('due_date', 'None')
        task_priority = task.get('priority', 'medium')
        formatted.append(f"- ID: {task_id}, Title: {task_title}, Due: {task_due}, Priority: {task_priority}")
    return "\n".join(formatted)

def match_task_id_by_reference(reference: str, tasks: List[Dict]) -> str:
    """Match a spoken reference to an existing task ID using fuzzy matching"""
    reference_lower = reference.lower().strip()
    
    # Simple fuzzy matching - find best match
    best_match = None
    best_score = 0
    
    for task in tasks:
        title = task.get('title', '').lower()
        # Simple word overlap scoring
        reference_words = set(reference_lower.split())
        title_words = set(title.split())
        
        if reference_words.intersection(title_words):
            score = len(reference_words.intersection(title_words)) / max(len(reference_words), len(title_words))
            if score > best_score:
                best_score = score
                best_match = task.get('id')
        
        # Also check if reference is a substring
        if reference_lower in title or title in reference_lower:
            score = min(len(reference_lower), len(title)) / max(len(reference_lower), len(title))
            if score > best_score:
                best_score = score
                best_match = task.get('id')
    
    return best_match if best_match and best_score > 0.3 else None

def parse_user_input(user_input: str, existing_tasks: List[Dict]) -> Dict:
    """Parse user input using Gemini and return structured JSON"""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    
    try:
        existing_tasks_formatted = format_existing_tasks_for_prompt(existing_tasks)
        current_datetime = get_current_datetime_str()
        
        prompt = PLANNER_PROMPT_TEMPLATE.format(
            current_datetime=current_datetime,
            user_input=user_input,
            existing_tasks=existing_tasks_formatted
        )
        full_prompt = SYSTEM_PROMPT + "\n\n" + prompt

        # Pick best MVP model (balance)
        model_name = "models/gemini-flash-latest"

        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt
        )

        response_text = (getattr(response, "text", "") or "").strip()
        if not response_text:
            raise Exception("Gemini returned empty response text (check model access / key / safety filters).")
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        result = json.loads(response_text)
        return result
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Gemini response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error calling Gemini API: {str(e)}")

def parse_voice_command(command: str, existing_tasks: List[Dict]) -> Dict:
    """Parse a specific voice command"""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    
    try:
        existing_tasks_formatted = format_existing_tasks_for_prompt(existing_tasks)
        current_datetime = get_current_datetime_str()
        
        prompt = COMMAND_PARSER_PROMPT_TEMPLATE.format(
            command=command,
            existing_tasks=existing_tasks_formatted,
            current_datetime=current_datetime
        )
        
        full_prompt = SYSTEM_PROMPT + "\n\n" + prompt

        model_name = "models/gemini-flash-latest"

        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt
        )

        response_text = (getattr(response, "text", "") or "").strip()
        if not response_text:
            raise Exception("Gemini returned empty response text (check model access / key / safety filters).")
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        result = json.loads(response_text)
        return result
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Gemini response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error calling Gemini API: {str(e)}")
