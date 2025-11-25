# Installing Dependencies

## Quick Fix for "ModuleNotFoundError"

The error means Python dependencies aren't installed. Follow these steps:

## Step 1: Navigate to Backend Directory

```bash
cd backend
```

## Step 2: Create Virtual Environment (Recommended)

### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Verify Installation

```bash
python -c "import fastapi; print('FastAPI installed!')"
```

## Step 5: Start Server

```bash
uvicorn app.main:app --reload
```

## Alternative: Install Without Virtual Environment

If you prefer not to use a virtual environment:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Troubleshooting

### "pip not found"
- Use `python -m pip` instead of `pip`
- Or `python3 -m pip` on Linux/Mac

### "Permission denied"
- Use `pip install --user -r requirements.txt`
- Or activate virtual environment first

### Still getting errors?
- Make sure you're in the `backend` directory
- Check Python version: `python --version` (should be 3.11+)
- Try: `python -m pip install --upgrade pip` first

