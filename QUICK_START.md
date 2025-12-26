# Quick Start Guide - NeverMiss

## Why Can't I See the Users Table?

**Answer:** You need to run the SQL script in Supabase to create the tables. The SQL file is just code - you must execute it in Supabase SQL Editor.

### How to Create the Users Table:

1. **Go to Supabase Dashboard**
   - Open [supabase.com](https://supabase.com)
   - Sign in and open your project

2. **Open SQL Editor**
   - Click **SQL Editor** in the left sidebar
   - Click **New Query**

3. **Run the Schema**
   - Open `supabase_schema.sql` from your NeverMiss folder
   - Copy ALL the contents
   - Paste into SQL Editor
   - Click **Run** (or press Ctrl+Enter)

4. **Verify Tables Created**
   - Click **Table Editor** in the left sidebar
   - You should now see three tables:
     - ✅ `users` (for authentication)
     - ✅ `tasks` (for user tasks)
     - ✅ `transcripts` (for input history)

**Note:** You don't need to commit anything to Git for database changes. SQL scripts are run directly in Supabase.

---

## Security: API Keys Protection

✅ **Your API keys are already protected!**

The `.env` file is already in `.gitignore`, which means:
- ✅ Git will NOT track your `.env` file
- ✅ Your API keys will NOT be committed to the repository
- ✅ Only the template (`config_template.env`) should be committed

**To verify:**
- Check `.gitignore` file - you should see `.env` listed
- When you run `git status`, `.env` should not appear

**Best Practice:**
- ✅ Commit `config_template.env` (template with placeholder values)
- ❌ Never commit your actual `.env` file (with real API keys)

---

## How to Run the Application

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Streamlit (web framework)
- Supabase (database)
- Google Generative AI (for text + audio)
- bcrypt (password hashing)
- Other dependencies

### Step 2: Set Up Database

1. Run `supabase_schema.sql` in Supabase SQL Editor (see above)
2. Verify you see `users`, `tasks`, and `transcripts` tables

### Step 3: Configure Environment Variables

1. Copy `config_template.env` to `.env`
2. Fill in your values:
   - `SUPABASE_URL` - From Supabase Settings > API
   - `SUPABASE_KEY` - From Supabase Settings > API
   - `GEMINI_API_KEY` - From Google AI Studio (REQUIRED)
   - `SMTP_EMAIL` and `SMTP_PASSWORD` - Optional (for email)

### Step 4: Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Step 5: Create Account

1. Click "Join here" on the landing page
2. Enter email and password
3. Click "Sign Up"
4. ✅ You're automatically logged in!

---

## Current Features

### ✅ Custom Authentication
- Users stored in `users` table
- Passwords hashed with bcrypt
- No email verification needed
- Simple signup and login

### ✅ AI Processing
- **Text**: Gemini AI processes natural language
- **Audio**: Gemini transcribes audio files (WAV, MP3, OGG, FLAC)
- **Smart Parsing**: Extracts tasks, dates, priorities

### ✅ Password Reset
- Simple form: Email + New Password + Confirm Password
- Direct database update (no email links)
- Works immediately

### ✅ Task Management
- Multiple views: Today, Week, Upcoming, Completed, History
- Voice commands: "Mark X as done", "Snooze X for 2 hours"
- Priority levels: P0, High, Medium, Low

---

## Common Issues

### "Can't see users table"
→ Run the SQL script in Supabase SQL Editor (see above)

### "Module not found"
→ Run `pip install -r requirements.txt`

### "Authentication error"
→ Make sure `users` table exists (run SQL script)
→ Check Supabase credentials in `.env`

### "Audio transcription not working"
→ Check `GEMINI_API_KEY` is set in `.env`
→ Verify API key has quota

---

## Need More Help?

- **Detailed Setup**: See `RUN_INSTRUCTIONS.md`
- **Full Documentation**: See `README.md`
- **Authentication Details**: See `CUSTOM_AUTH_UPDATE.md`
- **Audio Transcription**: See `GEMINI_AUDIO_UPDATE.md`

---

**You're all set! 🚀**

