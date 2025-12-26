# Step-by-Step Instructions to Run NeverMiss

Follow these instructions in order to set up and run the NeverMiss application.

## Prerequisites Check

Before starting, make sure you have:
- ✅ Python 3.11 or higher installed (recommended)
- ✅ Internet connection
- ✅ Supabase account (free tier available)
- ✅ Google Gemini API key (free tier available)
- ✅ Gmail account (optional, for email reminders)

Check Python version:
```bash
python --version
```
If you don't have Python, download it from [python.org](https://www.python.org/downloads/)

---

## Step 1: Install Python Dependencies

Open your terminal/command prompt in the NeverMiss folder and run:

**If using virtual environment (recommended):**
```bash
.\venv\Scripts\Activate.ps1  # On Windows PowerShell
pip install -r requirements.txt
```

**If not using virtual environment:**
```bash
pip install -r requirements.txt
```

**Note:** If you get permission errors, try:
```bash
pip install --user -r requirements.txt
```

**Expected output:** All packages will be installed including:
- Streamlit
- Supabase
- Google Generative AI (for text processing AND audio transcription)
- bcrypt (for password hashing)
- python-dotenv
- pytz
- schedule

---

## Step 2: Set Up Supabase Database

### 2.1 Open Supabase Dashboard

1. Go to [supabase.com](https://supabase.com)
2. Sign in to your account
3. Open your project

### 2.2 Run Database Schema

**IMPORTANT:** You must run the SQL script directly in Supabase - this creates the database tables including the `users` table.

1. In Supabase Dashboard, click **SQL Editor** in the left sidebar
2. Click **New Query**
3. Open the file `supabase_schema.sql` from your NeverMiss folder
4. Copy the entire contents of `supabase_schema.sql`
5. Paste it into the SQL Editor
6. Click **Run** (or press Ctrl+Enter)
7. You should see "Success. No rows returned" - this is correct!

### 2.3 Verify Tables Created

1. Click **Table Editor** in the left sidebar
2. You should see **three tables**:
   - `users` (for custom authentication - stores user credentials)
   - `tasks` (stores user tasks)
   - `transcripts` (stores user input history)

✅ **Database is ready!**

**Note:** If you don't see the `users` table, make sure you ran the SQL script in Step 2.2. The schema creates all three tables.

---

## Step 3: Get Google Gemini API Key

**IMPORTANT:** Gemini API key is used for BOTH text processing AND audio transcription (speech-to-text).

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the API key (starts with `AIzaSy...`)

**Note:** Gemini free tier includes generous quotas for both text and audio processing.

---

## Step 4: Get Gmail App Password (Optional - for email reminders)

**IMPORTANT:** You cannot use your regular Gmail password. You need an App Password.

### 4.1 Enable 2-Step Verification (if not already enabled)

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", find **2-Step Verification**
3. If it says "Off", click it and follow the prompts to enable it
4. If it's already "On", skip to step 4.2

### 4.2 Generate App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click **App passwords**
   - If you don't see "App passwords", make sure 2-Step Verification is enabled first
3. You may need to sign in again
4. Select "Mail" from the dropdown
5. Select "Other (Custom name)" from device dropdown
6. Type: **NeverMiss**
7. Click **Generate**
8. You'll see a 16-character password like: `abcd efgh ijkl mnop`
9. **Copy this password** (remove the spaces when copying)

### 4.3 Update .env File

1. Open the `.env` file in your NeverMiss folder
2. Find the line: `SMTP_PASSWORD=YOUR_GMAIL_APP_PASSWORD_HERE`
3. Replace `YOUR_GMAIL_APP_PASSWORD_HERE` with your 16-character App Password (no spaces)
4. Save the file

**Example:**
```env
SMTP_PASSWORD=abcdefghijklmnop
```

---

## Step 5: Verify .env File Configuration

Create a `.env` file in the NeverMiss folder (copy from `config_template.env`) and make sure it looks like this:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Gemini API Configuration (used for both text generation and audio transcription)
GEMINI_API_KEY=your_gemini_api_key_here

# Email Configuration (Optional - for email reminders)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_16_character_app_password_here
```

✅ **Important Notes:**
- `GEMINI_API_KEY` is REQUIRED (used for both text and audio processing)
- `SMTP_PASSWORD` is OPTIONAL (only needed for email reminders)
- The `.env` file is already in `.gitignore` to protect your API keys

---

## Step 6: Run the Application

1. Open terminal/command prompt in the NeverMiss folder

2. **If using virtual environment:**
   ```bash
   .\venv\Scripts\Activate.ps1  # On Windows PowerShell
   streamlit run app.py
   ```

3. **If not using virtual environment:**
   ```bash
   streamlit run app.py
   ```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

4. Your browser should automatically open to `http://localhost:8501`
   - If it doesn't, manually open your browser and go to that URL

✅ **The app is now running!**

---

## Step 7: First Time Usage

### 7.1 Create Your Account

1. On the landing page, click **"Join here"** button
2. Enter your email address
3. Enter a password (must be at least 6 characters)
4. Confirm your password
5. Click **"Sign Up"**
6. ✅ You'll be automatically logged in and redirected to the main app!

**Note:** No email verification needed - you can use the app immediately after signup.

### 7.2 Sign In (if you logged out)

1. Enter your email and password
2. Click **"Log In"**
3. You'll be redirected to the main app interface!

### 7.3 Reset Password (if needed)

1. Click **"Forgot password?"** on the login page
2. Enter your email
3. Enter your new password
4. Confirm your new password
5. Click **"Reset Password"**
6. You'll be redirected to the login page to sign in with your new password

**Note:** No email links needed - password is updated directly in the database.

### 7.4 Add Your First Task

**Option 1: Text Input**
1. Type in the text box at the bottom: `"Buy groceries tomorrow"`
2. Click **"Send"**
3. The AI (Gemini) will process and add your task!

**Option 2: Voice Input (Audio Transcription)**
1. Click **"Or record audio"** below the text box
2. Upload an audio file (WAV, MP3, OGG, or FLAC)
3. Click **"Send"**
4. The audio will be transcribed using Gemini and processed!

---

## Troubleshooting

### Problem: "Module not found" error

**Solution:**
```bash
pip install -r requirements.txt
```

Make sure you're in the virtual environment if you're using one.

### Problem: Can't see `users` table in Supabase

**Solution:**
- Make sure you ran the SQL script from `supabase_schema.sql` in Supabase SQL Editor
- Refresh the Table Editor page
- You should see three tables: `users`, `tasks`, and `transcripts`

### Problem: Can't connect to Supabase

**Solution:**
- Verify your `SUPABASE_URL` and `SUPABASE_KEY` in `.env` are correct
- Check your internet connection
- Make sure you ran the SQL schema in Supabase (Step 2.2)

### Problem: Authentication error / Can't sign up or login

**Solution:**
- Make sure the `users` table exists in Supabase (run the SQL schema if needed)
- Check that your Supabase credentials in `.env` are correct
- Try clearing browser cookies and signing up again

### Problem: Email not working / SMTP error

**Solution:**
- Make sure you're using an App Password, not your regular Gmail password
- Verify 2-Step Verification is enabled on your Google account
- Check that `SMTP_PASSWORD` in `.env` is exactly 16 characters (no spaces)
- Email is optional - the app works without it

### Problem: Speech-to-text (audio transcription) not working

**Solution:**
- Make sure `GEMINI_API_KEY` is set in your `.env` file
- Verify your Gemini API key is valid and has quota available
- Check the error message in the terminal for specific issues
- Supported formats: WAV, MP3, OGG, FLAC

### Problem: Port 8501 already in use

**Solution:**
Run on a different port:
```bash
streamlit run app.py --server.port 8502
```

---

## Next Steps After Running

1. ✅ Explore the different views: Today, Week, Upcoming, Completed, History
2. ✅ Try voice commands: "Mark meeting prep as done", "Snooze groceries for 2 hours"
3. ✅ Test audio transcription by uploading an audio file
4. ✅ Test email notifications by creating/updating tasks (if email is configured)
5. ✅ Set up daily email scheduler (optional, see README.md)

---

## Stopping the Application

To stop the application:
1. Go back to your terminal/command prompt
2. Press `Ctrl + C`
3. Confirm by pressing `Y` if prompted

---

## Security Notes

✅ **API Keys are Protected:**
- The `.env` file is already in `.gitignore`
- Never commit API keys to Git
- Share `config_template.env` (template) but never your actual `.env` file

✅ **Password Security:**
- All passwords are hashed using bcrypt before storage
- Passwords are never stored in plain text
- Password verification uses secure bcrypt comparison

---

## Need Help?

- Check `README.md` for detailed documentation
- Check `GMAIL_SETUP.md` for Gmail App Password help
- Check `CUSTOM_AUTH_UPDATE.md` for authentication details
- Check `GEMINI_AUDIO_UPDATE.md` for audio transcription details
- Review error messages in the terminal for specific issues

---

**You're all set! Enjoy using NeverMiss! ✅**
