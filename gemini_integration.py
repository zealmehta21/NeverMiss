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
User Timezone: {user_timezone}

CRITICAL TIMEZONE RULES - FOLLOW EXACTLY:
- User's timezone: {user_timezone}
- Current date/time in user's timezone: {current_datetime}

ABSOLUTE RULES - THE USER'S SPOKEN TIME IS AUTHORITATIVE:
1. When user says a time (e.g., "4pm", "10pm", "3pm", "1:00 PM"), output that EXACT hour in {user_timezone}
2. NEVER convert to UTC. NEVER use 'Z' suffix. NEVER output UTC times.
3. NEVER convert the hour. If user says "4pm", output hour=16 (4pm in 24-hour), NOT the UTC equivalent.
4. ALWAYS output with timezone offset for {user_timezone} (e.g., "-05:00", "-08:00", "-04:00")
5. Use 24-hour format for times (e.g., "10pm" = "22:00", "3pm" = "15:00", "4pm" = "16:00")

CRITICAL: The hour in your output MUST match what the user said:
- User says "4pm" → hour MUST be 16 (not 21, not 9, not any other number)
- User says "10pm" → hour MUST be 22 (not 3, not 15, not any other number)
- User says "3pm" → hour MUST be 15 (not 20, not 8, not any other number)

EXAMPLES:
- User says "4pm" in America/New_York on Jan 11, 2026:
  OUTPUT: "2026-01-11T16:00:00-05:00" (4pm EST, hour=16)
  NEVER: "2026-01-11T21:00:00Z" (9pm UTC - WRONG! hour changed from 16 to 21)
  NEVER: "2026-01-11T16:00:00Z" (UTC - WRONG! missing timezone offset)
  
- User says "10pm" in America/New_York on Jan 8, 2026:
  OUTPUT: "2026-01-08T22:00:00-05:00" (10pm EST, hour=22)
  NEVER: "2026-01-09T03:00:00Z" (3am UTC next day - WRONG! hour changed from 22 to 3)
  
- User says "3pm" in America/New_York:
  OUTPUT: "2026-01-08T15:00:00-05:00" (3pm EST, hour=15)
  NEVER: "2026-01-08T20:00:00Z" (8pm UTC - WRONG! hour changed from 15 to 20)

- User says "1:00 PM":
  OUTPUT: "2026-01-08T13:00:00-05:00" (1pm EST, hour=13)
  NEVER: UTC or any other timezone

Use {current_datetime} to determine the correct offset for today's date in {user_timezone}.

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
User Timezone: {user_timezone}

IMPORTANT: When the user mentions a time (e.g., "10am", "3pm", "2:30pm"), interpret it in the user's timezone ({user_timezone}).
Always output times in ISO 8601 format with the correct timezone offset.

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

def get_current_datetime_str(timezone: str) -> str:
    """
    Get current datetime string in the specified timezone.
    
    GUARDRAIL: NEVER use UTC unless explicitly required.
    If timezone is UTC, log and use America/New_York as fallback.
    """
    # GUARDRAIL: Fail loudly if timezone is UTC unexpectedly
    if timezone == "UTC":
        timezone = "America/New_York"
    
    try:
        tz = pytz.timezone(timezone)
        return datetime.now(tz).isoformat()
    except Exception as e:
        tz = pytz.timezone("America/New_York")
        return datetime.now(tz).isoformat()

def normalize_datetime_to_timezone(dt_str: str, target_timezone: str) -> str:
    """
    Normalize a datetime string to a specific timezone.
    
    ABSOLUTE RULES (NO EXCEPTIONS):
    1. SPOKEN TIME IS AUTHORITATIVE - NEVER convert it
    2. NEVER convert spoken times to UTC
    3. NEVER trust Gemini's timezone math
    4. NEVER call astimezone() on spoken times
    5. ALWAYS rebuild datetime using localize() in user's timezone
    
    This function:
    - Strips ALL timezone info from Gemini output
    - Extracts ONLY: year, month, day, hour, minute
    - Rebuilds datetime using localize() - NEVER converts
    """
    if not dt_str:
        return None
    
    try:
        target_tz = pytz.timezone(target_timezone)
        
        # STEP 1: Strip ALL timezone information completely
        import re
        # Remove 'Z' (UTC marker)
        dt_str_clean = dt_str.replace('Z', '')
        # Remove timezone offsets like +00:00, -05:00, +08:00
        dt_str_clean = re.sub(r'[+-]\d{2}:\d{2}$', '', dt_str_clean)
        # Remove microseconds if present
        if '.' in dt_str_clean:
            dt_str_clean = dt_str_clean.split('.')[0]
        
        # STEP 2: Parse ONLY date/time components (year, month, day, hour, minute, second)
        # Extract components manually to be absolutely sure
        try:
            if 'T' in dt_str_clean:
                date_part, time_part = dt_str_clean.split('T')
                year, month, day = map(int, date_part.split('-'))
                time_components = time_part.split(':')
                hour = int(time_components[0])
                minute = int(time_components[1]) if len(time_components) > 1 else 0
                second = int(time_components[2]) if len(time_components) > 2 else 0
            else:
                # Just a date
                year, month, day = map(int, dt_str_clean.split('-'))
                now = datetime.now(target_tz)
                hour = now.hour
                minute = now.minute
                second = now.second
        except (ValueError, IndexError) as e:
            # Fallback: try fromisoformat, but extract components to avoid any timezone issues
            try:
                # Use fromisoformat but immediately extract components (don't trust it for timezone)
                dt_naive = datetime.fromisoformat(dt_str_clean.split('.')[0])
                # CRITICAL: Extract components directly - don't use dt_naive if it has timezone
                # If fromisoformat created a timezone-aware datetime, we need to be careful
                if dt_naive.tzinfo is not None:
                    # This shouldn't happen if we stripped timezone, but handle it
                    # Convert to naive by extracting components
                    year, month, day = dt_naive.year, dt_naive.month, dt_naive.day
                    hour, minute, second = dt_naive.hour, dt_naive.minute, dt_naive.second or 0
                else:
                    # Naive datetime - safe to use
                    year, month, day = dt_naive.year, dt_naive.month, dt_naive.day
                    hour, minute, second = dt_naive.hour, dt_naive.minute, dt_naive.second or 0
            except Exception as e2:
                raise ValueError(f"Cannot parse datetime components from: {dt_str_clean}. Error: {e}, {e2}")
        
        # STEP 3: Rebuild datetime in target timezone with EXACT hour/minute
        # CRITICAL: Use localize() - NEVER astimezone()
        # This creates a NEW datetime in target timezone with the exact hour/minute
        dt = target_tz.localize(datetime(year, month, day, hour, minute, second))
        
        # STEP 4: GUARDRAIL - Verify hour is preserved (should always be true with localize())
        # This is a safety check - localize() should never change the hour
        if dt.hour != hour:
            error_msg = f"CRITICAL ERROR: Hour mismatch! Input hour: {hour}, Output hour: {dt.hour}. Input: {dt_str}, Cleaned: {dt_str_clean}, Components: {year}-{month}-{day} {hour}:{minute}:{second}, Timezone: {target_timezone}"
            # This should never happen with localize(), but if it does, raise an error
            raise ValueError(error_msg)
        
        # STEP 5: Return ISO format with correct DST-aware offset
        result = dt.isoformat()
        return result
        
    except Exception as e:
        return dt_str

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

def parse_user_input(user_input: str, existing_tasks: List[Dict], user_timezone: str) -> Dict:
    """
    Parse user input using Gemini and return structured JSON.
    
    REQUIRED: user_timezone must be a valid timezone (e.g., 'America/New_York').
    NEVER pass 'UTC' - this will cause incorrect time parsing.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    
    if not user_timezone:
        raise ValueError("CRITICAL ERROR: user_timezone is required and cannot be empty!")
    
    # GUARDRAIL: Assert timezone is NOT UTC before sending to Gemini
    if user_timezone == "UTC":
        raise ValueError("CRITICAL ERROR: user_timezone is UTC! Cannot parse times correctly. Must use a real timezone like 'America/New_York'.")
    
    try:
        existing_tasks_formatted = format_existing_tasks_for_prompt(existing_tasks)
        current_datetime = get_current_datetime_str(user_timezone)
        
        prompt = PLANNER_PROMPT_TEMPLATE.format(
            current_datetime=current_datetime,
            user_timezone=user_timezone,
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

def parse_voice_command(command: str, existing_tasks: List[Dict], user_timezone: str) -> Dict:
    """
    Parse a specific voice command.
    
    REQUIRED: user_timezone must be a valid timezone (e.g., 'America/New_York').
    NEVER pass 'UTC' - this will cause incorrect time parsing.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    
    if not user_timezone:
        raise ValueError("CRITICAL ERROR: user_timezone is required and cannot be empty!")
    
    # GUARDRAIL: Assert timezone is NOT UTC before sending to Gemini
    if user_timezone == "UTC":
        raise ValueError("CRITICAL ERROR: user_timezone is UTC! Cannot parse times correctly. Must use a real timezone like 'America/New_York'.")
    
    try:
        existing_tasks_formatted = format_existing_tasks_for_prompt(existing_tasks)
        current_datetime = get_current_datetime_str(user_timezone)
        
        prompt = COMMAND_PARSER_PROMPT_TEMPLATE.format(
            command=command,
            existing_tasks=existing_tasks_formatted,
            current_datetime=current_datetime,
            user_timezone=user_timezone
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
