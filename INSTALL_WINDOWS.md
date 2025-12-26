# Windows Installation Guide - Fixing Build Tools Error

If you're getting the "Microsoft Visual C++ 14.0 or greater is required" error, follow these steps:

## Quick Fix (Recommended)

### Option 1: Install Visual C++ Build Tools

1. **Download Microsoft C++ Build Tools:**
   - Go to: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Click "Download Build Tools"
   - Run the installer

2. **Install Options:**
   - Select "C++ build tools" workload
   - Make sure "MSVC v143 - VS 2022 C++ x64/x86 build tools" is checked
   - Click "Install"

3. **After Installation:**
   - Close and restart your terminal/command prompt
   - Run: `pip install -r requirements.txt`

### Option 2: Install Individual Packages (Workaround)

If you can't install Build Tools, try installing packages individually:

```bash
# Install core packages first
pip install streamlit
pip install python-dotenv
pip install pytz
pip install schedule

# Install Google AI
pip install google-generativeai

# Install OpenAI
pip install openai

# Try Supabase (may fail on storage dependencies, but core will work)
pip install supabase
```

If Supabase installation fails, install dependencies separately:

```bash
pip install httpx>=0.26
pip install postgrest
pip install realtime
pip install supabase-auth
```

The app should work with these core dependencies. Storage features might be limited, but authentication and database operations should work.

### Option 3: Use Pre-built Wheels

Try forcing pip to use pre-built wheels:

```bash
pip install --only-binary :all: -r requirements.txt
```

---

## Verify Installation

After installation, run:

```bash
python check_setup.py
```

This will show you what's installed and what's missing.

---

## Alternative: Use WSL (Windows Subsystem for Linux)

If you have WSL installed:

1. Open WSL terminal
2. Navigate to your project: `cd /mnt/c/Users/Zeal/NeverMiss`
3. Install Python and pip if needed
4. Run: `pip install -r requirements.txt`

This avoids Windows build tools issues entirely.

---

## Still Stuck?

The app will work even if some optional dependencies fail. The core functionality (authentication, database, Gemini AI) should work without the problematic `pyroaring` package.

Try running the app anyway:
```bash
streamlit run app.py
```

If you see import errors for specific modules, we can address those individually.
