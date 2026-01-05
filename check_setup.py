"""
Diagnostic script to check if Skkadoosh is set up correctly
"""
import sys
import os

print("=" * 60)
print("Skkadoosh Setup Diagnostic Check")
print("=" * 60)
print()

# Check Python version
print("1. Checking Python version...")
python_version = sys.version_info
print(f"   Python {python_version.major}.{python_version.minor}.{python_version.micro}")
if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
    print("   WARNING: Python 3.8+ required")
else:
    print("   OK: Python version is compatible")
print()

# Check required packages
print("2. Checking required packages...")
required_packages = {
    'streamlit': 'streamlit',
    'supabase': 'supabase',
    'genai': 'genai',
    'openai': 'openai',
    'dotenv': 'python-dotenv',
    'pytz': 'pytz'
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
        print(f"   OK: {package}")
    except ImportError:
        print(f"   MISSING: {package} - NOT INSTALLED")
        missing_packages.append(package)

if missing_packages:
    print(f"\n   WARNING: Missing packages: {', '.join(missing_packages)}")
    print("   Run: pip install -r requirements.txt")
print()

# Check .env file
print("3. Checking .env file...")
if os.path.exists('.env'):
    print("   OK: .env file exists")
    
    # Load .env and check values
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL', ''),
        'SUPABASE_KEY': os.getenv('SUPABASE_KEY', ''),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
        'SMTP_EMAIL': os.getenv('SMTP_EMAIL', ''),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', ''),
    }
    
    for key, value in env_vars.items():
        if value:
            if key == 'SMTP_PASSWORD' and value == 'YOUR_GMAIL_APP_PASSWORD_HERE':
                print(f"   WARNING: {key}: Not configured (still has placeholder)")
            else:
                # Show first 10 chars for security
                display_value = value[:10] + "..." if len(value) > 10 else value
                print(f"   OK: {key}: {display_value}")
        else:
            print(f"   MISSING: {key}: Not set")
else:
    print("   ERROR: .env file NOT FOUND")
    print("   Create .env file from config_template.env")
print()

# Check config import
print("4. Checking configuration...")
try:
    import config
    print("   OK: config.py imports successfully")
    
    if not config.SUPABASE_URL:
        print("   ERROR: SUPABASE_URL not set in config")
    if not config.SUPABASE_KEY:
        print("   ERROR: SUPABASE_KEY not set in config")
    if not config.GEMINI_API_KEY:
        print("   ERROR: GEMINI_API_KEY not set in config")
except Exception as e:
    print(f"   ERROR: Error importing config: {e}")
print()

# Check database connection
print("5. Testing Supabase connection...")
try:
    from database import get_supabase_client
    client = get_supabase_client()
    print("   OK: Supabase client created successfully")
except Exception as e:
    print(f"   ERROR: Error connecting to Supabase: {e}")
    print("   Check your SUPABASE_URL and SUPABASE_KEY in .env")
print()

# Check Gemini API
print("6. Testing Gemini API key...")
try:
    from google import genai
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    if gemini_key:
        genai.configure(api_key=gemini_key)
        print("   OK: Gemini API configured")
    else:
        print("   ERROR: GEMINI_API_KEY not set")
except Exception as e:
    print(f"   WARNING: Gemini API check: {e}")
print()

print("=" * 60)
if missing_packages:
    print("SETUP INCOMPLETE - Install missing packages")
    print(f"   Run: pip install {' '.join(missing_packages)}")
else:
    print("Basic setup looks good!")
    print("   You can try running: streamlit run app.py")
print("=" * 60)
