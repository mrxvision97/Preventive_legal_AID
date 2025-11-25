# Quick Fix: ModuleNotFoundError: No module named 'fastapi'

## 🚀 Quick Solution (Windows)

Run these commands in PowerShell or Command Prompt:

```powershell
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment (if it doesn't exist)
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 5. Verify installation
python -c "import fastapi; print('FastAPI installed successfully!')"

# 6. Start server
python -m uvicorn app.main:app --reload
```

## ✅ One-Line Fix

If you already have a virtual environment:

```powershell
cd backend && venv\Scripts\activate && python -m pip install -r requirements.txt && python -m uvicorn app.main:app --reload
```

## 🔧 Alternative: Use the Batch Script

```powershell
cd backend
.\run_server.bat
```

This script will:
- Automatically activate venv if it exists
- Install dependencies if needed
- Start the server

## 📝 Step-by-Step Explanation

### Step 1: Check Current Directory
```powershell
cd backend
pwd  # Should show: ...\Preventive_legal\backend
```

### Step 2: Create/Activate Virtual Environment
```powershell
# Create if doesn't exist
if (-not (Test-Path venv)) {
    python -m venv venv
}

# Activate
venv\Scripts\activate

# You should see (venv) in your prompt
```

### Step 3: Install Dependencies
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
python -m pip install -r requirements.txt
```

### Step 4: Verify
```powershell
python -c "import fastapi, uvicorn; print('✅ All packages installed!')"
```

### Step 5: Start Server
```powershell
python -m uvicorn app.main:app --reload
```

## ⚠️ Common Issues

### Issue: "venv\Scripts\activate : The term is not recognized"

**Solution**: Use full path or check if venv exists:
```powershell
# Check if venv exists
Test-Path venv\Scripts\activate.bat

# If not, create it
python -m venv venv
```

### Issue: "pip is not recognized"

**Solution**: Use `python -m pip` instead:
```powershell
python -m pip install -r requirements.txt
```

### Issue: "Permission denied"

**Solution**: Run PowerShell as Administrator, or use:
```powershell
python -m pip install --user -r requirements.txt
```

### Issue: Still getting errors after installation

**Solution**: Make sure you're using the correct Python:
```powershell
# Check Python version
python --version  # Should be 3.11+

# Check which Python
where python

# Verify packages are installed
python -m pip list | Select-String fastapi
```

## 🎯 Quick Test

After fixing, test with:

```powershell
cd backend
venv\Scripts\activate
python -c "from fastapi import FastAPI; print('✅ FastAPI works!')"
python -m uvicorn app.main:app --reload
```

If you see "Application startup complete", you're good to go! 🎉

