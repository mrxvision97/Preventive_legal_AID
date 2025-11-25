# Fix: ModuleNotFoundError: No module named 'fastapi'

## Quick Fix

The error occurs because Python can't find the installed packages. Here are solutions:

## Solution 1: Install All Dependencies (Recommended)

```bash
cd backend
python -m pip install -r requirements.txt
```

## Solution 2: Use Python Module Syntax

Instead of:
```bash
uvicorn app.main:app --reload
```

Use:
```bash
python -m uvicorn app.main:app --reload
```

## Solution 3: Check Python Environment

Make sure you're using the same Python that has packages installed:

```bash
# Check which Python
python --version
where python

# Verify FastAPI is installed
python -c "import fastapi; print(fastapi.__version__)"
```

## Solution 4: Use Virtual Environment (Best Practice)

```bash
# Create virtual environment
cd backend
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn app.main:app --reload
```

## Solution 5: Use the Batch Script

On Windows, use the provided script:

```bash
cd backend
run_server.bat
```

## Common Issues

### Issue: "pip install" works but uvicorn can't find packages

**Cause**: Different Python interpreters

**Fix**: Use `python -m uvicorn` instead of just `uvicorn`

### Issue: Packages installed in user directory

**Fix**: Make sure you're using the same Python:
```bash
python -m pip list | findstr fastapi
```

### Issue: Multiple Python installations

**Fix**: Use full path or check PATH:
```bash
where python
python -m pip install -r requirements.txt
```

## Verify Installation

After installing, test:

```bash
python -c "import fastapi; import uvicorn; print('All packages installed!')"
```

If this works, then run:
```bash
python -m uvicorn app.main:app --reload
```

