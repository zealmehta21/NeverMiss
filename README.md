# NeverMiss - Voice-First Task Management

**Turn your voice into prioritized actions** - NeverMiss is an AI-powered task management web application built with Python and Streamlit. Speak or type your tasks, reminders, commitments, ideas, or project notes, and the AI converts them into an organized, prioritized task list.

## 🎯 Key Features

### Voice-First Task Management
- 🎤 **Audio Input**: Record or upload audio files to add tasks via voice
- 📝 **Text Input**: Type tasks directly in the chat-like interface
- 🤖 **AI Processing**: Gemini 3.0 intelligently parses and organizes your input
- ⚡ **Voice Commands**: Control tasks with natural voice commands

### Smart Task Organization
- 📅 **Time-based Views**: Today, This Week, Upcoming
- 🎯 **Priority Levels**: P0, High, Medium, Low
- ✅ **Task Actions**: Mark done, Edit, Snooze, Delete
- 📊 **Task Views**: Active, Completed, History

### Voice Commands
- **Mark Done**: "X is done", "I finished X"
- **Snooze**: "Snooze X for 2 hours", "Snooze X until tomorrow 9am"
- **Change Date**: "Move X to Friday 3pm"
- **Change Priority**: "Make X P0", "Lower priority of X"
- **Add Reminder**: "Remind me tomorrow at 11am to do X"

### Email Reminders
- 📧 Daily morning email with task list
- 📧 Email notifications when tasks are updated, deleted, or completed

## 🛠️ Technology Stack

- **Frontend/Backend**: Streamlit (Python web framework)
- **Database**: Supabase (PostgreSQL)
- **Speech-to-Text**: Google Gemini (audio transcription)
- **AI Processing**: Google Gemini (text + audio)
- **Authentication**: Custom (users table with bcrypt password hashing)
- **Password Security**: bcrypt

## 📋 Prerequisites

- Python 3.11 or higher (recommended)
- Supabase account (free tier available)
- Google Gemini API key (for text processing AND audio transcription)
- Email account for SMTP (optional, for email reminders)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd NeverMiss
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Supabase

1. Create a Supabase account at [supabase.com](https://supabase.com)
2. Create a new project
3. In the **SQL Editor**, run the SQL script from `supabase_schema.sql` to create the tables:
   - `users` (custom authentication)
   - `tasks` (user tasks)
   - `transcripts` (user input history)
4. Verify the tables in **Table Editor**
5. Note your project URL and anon key from **Settings > API**

**Important:** You must run the SQL script directly in Supabase SQL Editor - this creates all the necessary tables.

### 4. Get API Keys

#### Google Gemini API Key (REQUIRED)

**Used for:** Text processing AND audio transcription (speech-to-text)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key to your `.env` file

**Note:** Gemini free tier includes generous quotas for both text and audio processing.

#### Gmail App Password (OPTIONAL - for email reminders)

1. Enable 2-Step Verification on your Google account
2. Go to [Google Account Security](https://myaccount.google.com/security)
3. Click **App passwords**
4. Generate a new app password for "Mail"
5. Copy the 16-character password

### 5. Configure Environment Variables

1. Copy the template file:
   ```bash
   cp config_template.env .env
   ```
   (On Windows, copy the file manually)

2. Edit `.env` and add your credentials:
   ```env
   # Supabase Configuration
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key

   # Gemini API Configuration (REQUIRED - for text AND audio)
   GEMINI_API_KEY=your_gemini_api_key

   # Email Configuration (OPTIONAL)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_16_character_app_password
   ```

**Security Note:** The `.env` file is already in `.gitignore` to protect your API keys. Never commit it to Git.

## 🎮 Running the Application

### Development Mode

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

**First Time Setup:**
1. Sign up with your email and password
2. You'll be automatically logged in (no email verification needed)
3. Start adding tasks!

### Production Deployment

Deploy to Streamlit Cloud, Heroku, or any platform supporting Python:

1. Push your code to a Git repository
2. Connect to your deployment platform
3. Set environment variables in the platform's settings:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `GEMINI_API_KEY`
   - `SMTP_EMAIL` (optional)
   - `SMTP_PASSWORD` (optional)
4. Make sure to run the SQL schema in your Supabase project
5. Deploy!

## 📖 Usage Guide

### First Time Setup

1. **Sign Up**: Click "Join here" on the landing page
2. **Create Account**: Enter your email and password (must be at least 6 characters)
3. ✅ **Auto Login**: You'll be automatically logged in after signup (no email verification needed)

### Adding Tasks

#### Via Text Input
1. Type your task in the text input at the bottom
2. Click "Send"
3. Gemini AI will parse and organize your task

#### Via Voice/Audio
1. Click "Or record audio" and upload an audio file (WAV, MP3, OGG, FLAC)
2. The audio will be transcribed using Gemini
3. Click "Send" to process the transcription

### Managing Tasks

- **View Tasks**: Switch between Today, Week, Upcoming, Completed, or History views
- **Mark Done**: Click the ✓ button on a task
- **Edit Task**: Click the ✏️ button to edit title, description, priority, or due date
- **Snooze Task**: Click the ⏰ button to snooze for 2 hours, until tomorrow 9am, next week, or custom time
- **Delete Task**: Click the 🗑️ button to delete

### Voice Commands Examples

- "Buy groceries tomorrow"
- "Meeting prep is done"
- "Snooze dentist appointment for 2 hours"
- "Move project review to Friday 3pm"
- "Make quarterly report P0"
- "Remind me tomorrow at 11am to call Sarah"

## 📁 Project Structure

```
NeverMiss/
├── app.py                    # Main entry point
├── pages/
│   ├── 1_Landing.py         # Landing page
│   ├── 2_Main_App.py        # Main application
│   ├── 3_Signup.py          # Signup page
│   ├── 4_Login.py           # Login page
│   └── 5_Reset_Password.py  # Password reset page
├── config.py                 # Configuration loader
├── database.py               # Supabase database utilities
├── gemini_integration.py     # Gemini AI integration
├── whisper_integration.py    # Whisper STT integration
├── email_service.py          # Email functionality
├── utils.py                  # Utility functions
├── scheduler.py              # Daily email scheduler
├── supabase_schema.sql       # Database schema
├── config_template.env       # Environment variables template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🎨 Design System

The app uses a custom design system:

- **Colors**:
  - Primary: `#B88E23`
  - Secondary: `#5C4E3D`
  - Text: `#454240`
  - Background: `#FFFDFA`

- **Fonts**:
  - Headings: Libre Baskerville (Regular)
  - Body: DM Sans (Regular)

## 🔐 Security Notes

- Never commit your `.env` file to version control
- Use environment variables for all sensitive data
- Supabase Row Level Security (RLS) policies protect user data
- Audio files are not stored - only transcribed text is saved

## 📧 Email Reminders

To enable daily email reminders:

1. Set up SMTP credentials in `.env`
2. Run the scheduler script:
   ```bash
   python scheduler.py
   ```
3. Or set up a cron job to run the scheduler daily

## 🐛 Troubleshooting

### Authentication Issues
- Ensure Supabase URL and key are correct
- Check that email verification is not required (or verify your email)
- Clear browser cookies and try again

### API Errors
- Verify all API keys are correct in `.env`
- Check API quota/limits for OpenAI and Gemini
- Ensure internet connection is stable

### Audio Transcription Issues
- Use clear audio with minimal background noise
- Supported formats: WAV, MP3, OGG, FLAC
- Check OpenAI API key and quota

### Database Errors
- Verify Supabase connection details
- Ensure schema has been run in Supabase SQL editor
- Check RLS policies are set correctly

## 🔮 Future Enhancements

- Direct browser microphone recording (no file upload)
- Task categories and tags
- Collaboration features
- Mobile app
- Calendar integration
- Recurring tasks

## 📄 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**NeverMiss** - Never miss a task again! ✅

Built with ❤️ using Python and Streamlit