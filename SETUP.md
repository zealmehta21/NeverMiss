# NeverMiss Setup Guide

This guide will help you set up NeverMiss step-by-step.

## Quick Start Checklist

- [ ] Python 3.11+ installed
- [ ] Supabase account created
- [ ] Google Gemini API key obtained
- [ ] Email account for SMTP (optional, for email reminders)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `streamlit` - Web framework
- `supabase` - Database client
- `google-generativeai` - AI processing (text AND audio)
- `bcrypt` - Password hashing
- `python-dotenv` - Environment variables
- `pytz` - Timezone handling
- `schedule` - Task scheduling

### 2. Set Up Supabase

1. Go to [supabase.com](https://supabase.com) and sign up
2. Create a new project
3. Wait for the project to initialize (2-3 minutes)
4. Go to **SQL Editor**
5. Open `supabase_schema.sql` from your NeverMiss folder
6. Copy the entire contents
7. Paste and run it in the SQL Editor
8. Go to **Table Editor** and verify you see three tables:
   - `users` (custom authentication)
   - `tasks` (user tasks)
   - `transcripts` (user input history)
9. Go to **Settings > API**
10. Copy your Project URL and anon/public key

### 3. Get API Keys

#### Google Gemini API Key (REQUIRED)

**Used for:** Text processing AND audio transcription (speech-to-text)

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIzaSy...`)

**Note:** Gemini free tier includes generous quotas for both text and audio processing.

#### Gmail App Password (OPTIONAL - for email reminders)

1. Enable 2-Step Verification on your Google account
2. Go to [Google Account Security](https://myaccount.google.com/security)
3. Click **App passwords**
4. Generate a new app password for "Mail"
5. Copy the 16-character password

### 4. Configure Environment Variables

1. Copy `config_template.env` to `.env`:
   ```bash
   cp config_template.env .env
   ```
   (On Windows, you can copy the file manually)

2. Edit `.env` and fill in your values:
   ```env
   # Supabase Configuration
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   
   # Gemini API Configuration (REQUIRED - for text AND audio)
   GEMINI_API_KEY=AIzaSy...
   
   # Email Configuration (OPTIONAL)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_EMAIL=your.email@gmail.com
   SMTP_PASSWORD=your_16_character_app_password
   ```

**Important:**
- ✅ `GEMINI_API_KEY` is REQUIRED
- ✅ `.env` file is already in `.gitignore` (your API keys are protected)
- ⚠️ Never commit your `.env` file to Git

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### 6. Create Your First Account

1. Click **"Join here"** on the landing page
2. Enter your email and password
3. Click **"Sign Up"**
4. ✅ You'll be automatically logged in!

**Note:** No email verification needed - you can start using the app immediately.

## Features Overview

### Authentication System
- **Custom Authentication**: Users stored in `users` table
- **Secure Passwords**: Hashed with bcrypt
- **Simple Signup**: No email verification required
- **Direct Login**: Verify credentials against database
- **Password Reset**: Simple form, no email links needed

### AI Features
- **Text Processing**: Gemini AI understands natural language
- **Audio Transcription**: Gemini transcribes audio files (WAV, MP3, OGG, FLAC)
- **Smart Task Parsing**: Extracts tasks, priorities, dates from input
- **Voice Commands**: "Mark X as done", "Snooze X for 2 hours", etc.

### Task Management
- **Multiple Views**: Today, Week, Upcoming, Completed, History
- **Priority Levels**: P0, High, Medium, Low
- **Task Actions**: Mark done, Edit, Snooze, Delete
- **Smart Scheduling**: AI understands relative dates ("tomorrow", "next week")

## Troubleshooting

### "Module not found" errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Can't see `users` table in Supabase
- Make sure you ran the SQL schema in Supabase SQL Editor
- Refresh the Table Editor page
- You should see `users`, `tasks`, and `transcripts` tables

### Supabase connection errors
- Verify your URL and key are correct in `.env`
- Check that the schema has been run
- Ensure all three tables exist

### API errors
- Check your `GEMINI_API_KEY` is correct and has quota
- Verify your internet connection
- Check error messages in the terminal

### Authentication issues
- Make sure `users` table exists in Supabase
- Clear browser cookies
- Try signing up with a different email
- Check that passwords are at least 6 characters

### Audio transcription not working
- Verify `GEMINI_API_KEY` is set in `.env`
- Check that your API key has quota available
- Supported formats: WAV, MP3, OGG, FLAC
- Check error messages in terminal

## Technology Stack

- **Frontend/Backend**: Streamlit (Python web framework)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Custom (users table with bcrypt)
- **AI Processing**: Google Gemini (text + audio)
- **Password Security**: bcrypt hashing
- **Email**: SMTP (optional, for reminders)

## Security Features

✅ **API Keys**: Protected in `.env` (already in `.gitignore`)
✅ **Passwords**: Hashed with bcrypt (never stored in plain text)
✅ **Database**: Credentials stored securely in Supabase
✅ **Authentication**: Custom system with secure password verification

## Next Steps

- Read the main [README.md](README.md) for detailed usage instructions
- Check [RUN_INSTRUCTIONS.md](RUN_INSTRUCTIONS.md) for step-by-step setup
- Set up the daily email scheduler (see README) if desired
- Customize the design colors/fonts if desired

## Need Help?

- Check `RUN_INSTRUCTIONS.md` for detailed setup steps
- Review `CUSTOM_AUTH_UPDATE.md` for authentication details
- Review `GEMINI_AUDIO_UPDATE.md` for audio transcription info
- Check error messages in terminal for specific issues
- Open an issue on GitHub if you find a bug

Happy task managing! ✅
