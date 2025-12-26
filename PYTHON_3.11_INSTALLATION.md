# Installing Python 3.11 on Windows

## Method 1: Direct Download and Install (Recommended)

1. **Download Python 3.11:**
   - Go to: https://www.python.org/downloads/release/python-31111/
   - Scroll down to "Files" section
   - Download: **Windows installer (64-bit)** (or 32-bit if you have a 32-bit system)
   - The file will be named something like: `python-3.11.11-amd64.exe`

2. **Install Python 3.11:**
   - Run the downloaded installer
   - **IMPORTANT:** Check the box "Add Python 3.11 to PATH" at the bottom
   - Click "Install Now" (or "Customize installation" if you want to change the install location)
   - Wait for installation to complete

3. **Verify Installation:**
   ```powershell
   py -3.11 --version
   ```
   Should show: `Python 3.11.x`

## Method 2: Using Python Launcher (After Installation)

Once Python 3.11 is installed, you can use it with the Python launcher:

```powershell
# Check available Python versions
py --list

# Use Python 3.11 specifically
py -3.11 --version

# Run a script with Python 3.11
py -3.11 your_script.py

# Create virtual environment with Python 3.11
py -3.11 -m venv venv
```

## Setting Up Your Project with Python 3.11

### Option A: Create a Virtual Environment with Python 3.11

1. **Create virtual environment:**
   ```powershell
   py -3.11 -m venv venv
   ```

2. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Verify Python version:**
   ```powershell
   python --version
   ```
   Should show: `Python 3.11.x`

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

### Option B: Make Python 3.11 Default (Optional)

If you want Python 3.11 to be your default Python:

1. **Check current PATH:**
   ```powershell
   $env:PATH -split ';' | Select-String python
   ```

2. **Reorder PATH** (Python 3.11 should come before Python 3.14):
   - Open System Properties → Environment Variables
   - Edit "Path" in User variables
   - Move Python 3.11 entries above Python 3.14 entries
   - Click OK and restart terminal

## Quick Commands Reference

```powershell
# Check all installed Python versions
py --list

# Use Python 3.11
py -3.11

# Create venv with Python 3.11
py -3.11 -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Deactivate venv
deactivate
```

## Troubleshooting

### Problem: "py -3.11" not found
**Solution:** Make sure Python 3.11 is installed and the Python launcher can find it. Try reinstalling Python 3.11 with "Add to PATH" checked.

### Problem: Virtual environment still uses Python 3.14
**Solution:** Delete the existing venv folder and recreate it:
```powershell
Remove-Item -Recurse -Force venv
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

### Problem: Permission denied when activating venv
**Solution:** Run PowerShell as Administrator, or change execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

