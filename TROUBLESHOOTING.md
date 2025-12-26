# Troubleshooting Guide - Common Errors

## Error: Microsoft Visual C++ 14.0 or greater is required

**Problem:**
```
error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools"
```

**Solution 1: Install Build Tools (Recommended)**

1. Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. During installation, select "C++ build tools" workload
3. After installation, restart your terminal
4. Run `pip install -r requirements.txt` again

**Solution 2: Install Pre-built Wheel (Faster)**

Try installing without the problematic dependency first:

```bash
pip install streamlit supabase google-generativeai openai python-dotenv pytz schedule --no-deps
pip install streamlit supabase google-generativeai openai python-dotenv pytz schedule
```

If that doesn't work, you can try installing packages one by one, skipping the storage features:

```bash
pip install streamlit
pip install supabase
pip install google-generativeai
pip install openai
pip install python-dotenv
pip install pytz
pip install schedule
```

**Solution 3: Use Alternative Installation (If storage not needed)**

If you don't need Supabase storage features immediately, you can install a minimal set:

```bash
pip install streamlit>=1.28.0
pip install supabase>=2.0.0 --no-deps
pip install google-generativeai>=0.3.0
pip install openai>=1.0.0
pip install python-dotenv>=1.0.0
pip install pytz>=2023.3
pip install schedule>=1.2.0
```

Then manually install Supabase dependencies:
```bash
pip install httpx postgrest realtime supabase-auth supabase-functions
```

---

## Error: ModuleNotFoundError: No module named 'X'

**Problem:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
Install the missing module:
```bash
pip install streamlit
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

---

## Error: Supabase connection failed

**Problem:**
```
Error connecting to Supabase: ...
```

**Solutions:**
1. Check your `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`
2. Verify your Supabase project is active
3. Make sure you've run the SQL schema in Supabase (see `supabase_schema.sql`)
4. Check your internet connection

---

## Error: Gemini API key invalid

**Problem:**
```
Error calling Gemini API: ...
```

**Solutions:**
1. Verify `GEMINI_API_KEY` in `.env` is correct
2. Check if API key has expired or been revoked
3. Verify you have API quota available
4. Regenerate API key if needed

---

## Error: Port 8501 already in use

**Problem:**
```
Port 8501 is already in use
```

**Solution:**
Run on a different port:
```bash
streamlit run app.py --server.port 8502
```

Or kill the process using port 8501:
```bash
# Find process using port 8501
netstat -ano | findstr :8501
# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

---

## Error: SMTP authentication failed

**Problem:**
```
Error sending email: ...
SMTP Authentication failed
```

**Solutions:**
1. Make sure you're using Gmail App Password, NOT your regular password
2. Verify 2-Step Verification is enabled on Google Account
3. Check `SMTP_PASSWORD` in `.env` is exactly 16 characters (no spaces)
4. See `GMAIL_SETUP.md` for detailed instructions

---

## Error: .env file not found

**Problem:**
```
FileNotFoundError: .env
```

**Solution:**
1. Make sure `.env` file exists in the same directory as `app.py`
2. Copy from template: Check if `config_template.env` exists and copy it to `.env`
3. Create manually with your credentials (see `RUN_INSTRUCTIONS.md`)

---

## Error: UnicodeEncodeError in terminal

**Problem:**
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Solution:**
This is a Windows terminal encoding issue. The app will still work, but some characters may not display correctly. You can ignore this error or change terminal encoding:
```bash
chcp 65001
```

---

## Still having issues?

1. Run the diagnostic script:
   ```bash
   python check_setup.py
   ```

2. Check that all files are in place:
   - `app.py`
   - `config.py`
   - `.env` (should exist, not in git)
   - `requirements.txt`
   - `pages/` folder with all page files

3. Verify Python version:
   ```bash
   python --version
   ```
   Should be 3.8 or higher

4. Try running with verbose errors:
   ```bash
   python -v app.py
   ```

5. Check Streamlit directly:
   ```bash
   streamlit --version
   ```

---

## Quick Fix Checklist

- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file exists and has all required keys
- [ ] Supabase SQL schema has been run
- [ ] Gmail App Password is set (for email features)
- [ ] Internet connection is active
- [ ] Python 3.8+ is installed
