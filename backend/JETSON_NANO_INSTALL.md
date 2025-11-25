# Jetson Nano Installation Guide

This guide will help you install all dependencies for the Preventive Legal AID application on Jetson Nano.

## Prerequisites

- Jetson Nano with JetPack 4.6+ or JetPack 5.x
- Python 3.8 or higher
- Internet connection for initial setup

## Step 1: Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

## Step 2: Install System Dependencies

```bash
# Essential build tools
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget

# Image processing libraries
sudo apt-get install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev

# Tesseract OCR (optional - for offline OCR fallback)
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin
```

## Step 3: Create Virtual Environment

```bash
cd ~/Preventive_legal/backend
python3 -m venv venv
source venv/bin/activate
```

## Step 4: Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

## Step 5: Install Python Dependencies

```bash
# Install from Jetson Nano optimized requirements
pip install -r requirements-jetson-nano.txt
```

**Note:** If you encounter any errors, try installing packages one by one or use `--no-cache-dir` flag:

```bash
pip install --no-cache-dir -r requirements-jetson-nano.txt
```

## Step 6: Install Ollama (for Offline Mode)

If you want to use offline mode with Ollama:

```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve

# In another terminal, download the model
ollama pull qwen:0.5b
```

## Step 7: Configure Environment

Create `.env` file in `backend/` directory:

```bash
cd ~/Preventive_legal/backend
nano .env
```

Add your configuration:

```env
# OpenAI API Key (Required for OCR and AI analysis)
OPENAI_API_KEY=sk-your-api-key-here

# OpenAI Model (Fast and cost-effective)
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=2000

# Ollama (for offline mode)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen:0.5b
USE_OFFLINE_MODE=False

# Redis (Optional - for caching)
REDIS_HOST=redis-11431.c305.ap-south-1-1.ec2.cloud.redislabs.com
REDIS_PORT=11431
REDIS_USERNAME=default
REDIS_PASSWORD=your-redis-password

# Application Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## Step 8: Test Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Test FastAPI installation
python -c "import fastapi; print('FastAPI installed successfully')"

# Test OpenAI installation
python -c "import openai; print('OpenAI installed successfully')"

# Test OCR service
python -c "from app.services.ocr_service import extract_text_from_image; print('OCR service ready')"
```

## Step 9: Run the Application

```bash
# Make sure you're in the backend directory
cd ~/Preventive_legal/backend

# Activate virtual environment
source venv/bin/activate

# Run the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Troubleshooting

### Issue: pip install fails with "No module named '_ctypes'"

**Solution:**
```bash
sudo apt-get install -y libffi-dev
```

### Issue: Pillow installation fails

**Solution:**
```bash
sudo apt-get install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev
pip install --no-cache-dir Pillow==10.1.0
```

### Issue: Out of memory during installation

**Solution:**
```bash
# Increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make it permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Issue: OpenAI package installation is slow

**Solution:**
```bash
# Install with no cache to save space
pip install --no-cache-dir openai==1.3.5
```

### Issue: Tesseract not found

**Solution:**
```bash
# Install Tesseract system package
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin

# Then install Python wrapper
pip install pytesseract==0.3.10
```

## Optional: Install Additional Packages

### For Offline Voice Processing (Heavy - may not work on 4GB)

```bash
# Install PyTorch for ARM64 (Jetson)
# Download from NVIDIA or use pip with specific wheel
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Then install Whisper
pip install openai-whisper==20231117
pip install pyttsx3==2.90
```

### For PDF Processing

```bash
pip install PyPDF2==3.0.1 pdfplumber==0.10.3
```

### For AWS S3 Storage

```bash
pip install boto3==1.29.7 botocore==1.32.7
```

## Performance Optimization for Jetson Nano

1. **Disable RAG** (already disabled by default):
   ```env
   ENABLE_RAG=False
   ```

2. **Use smaller models**:
   ```env
   OPENAI_MODEL=gpt-4o-mini
   OLLAMA_MODEL=qwen:0.5b
   ```

3. **Reduce token limits**:
   ```env
   OPENAI_MAX_TOKENS=2000
   ```

4. **Use cloud Redis** (already configured):
   - No local Redis installation needed
   - Uses Redis Labs cloud instance

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All packages installed successfully
- [ ] `.env` file configured with API keys
- [ ] FastAPI server starts without errors
- [ ] OCR endpoint works (test with image upload)
- [ ] AI analysis endpoint works (test with text query)

## Next Steps

1. Set up the frontend (see main README)
2. Configure nginx (optional, for production)
3. Set up systemd service (optional, for auto-start)

## Support

If you encounter issues:
1. Check the error logs
2. Verify all system dependencies are installed
3. Ensure virtual environment is activated
4. Check `.env` file configuration
5. Review the main README for additional setup steps

