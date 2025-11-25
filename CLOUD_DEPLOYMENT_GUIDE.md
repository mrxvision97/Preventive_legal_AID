# Cloud Deployment Guide - VU Legal AID

## 📋 Deployment Architecture Options

This guide covers different ways to deploy VU Legal AID, including cloud deployment and hybrid architectures with Jetson Nano.

---

## 🏗️ Architecture Options

### Option 1: Full Cloud Deployment
**Backend + Frontend in Cloud, Jetson Nano as Client**

```
┌─────────────────┐
│   Cloud (AWS/   │
│   Azure/GCP)    │
│                 │
│  ┌───────────┐  │
│  │ Backend   │  │
│  │ (FastAPI) │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │ Frontend  │  │
│  │ (React)   │  │
│  └───────────┘  │
└────────┬────────┘
         │
         │ HTTP/HTTPS
         │
┌────────▼────────┐
│  Jetson Nano    │
│  (Browser/      │
│   Kiosk Mode)   │
└─────────────────┘
```

**Pros:**
- ✅ Centralized management
- ✅ Easy updates
- ✅ Scalable
- ✅ No local processing needed

**Cons:**
- ❌ Requires internet connection
- ❌ Higher latency
- ❌ Cloud costs

---

### Option 2: Hybrid Architecture (Recommended)
**Cloud Backend, Jetson Nano Frontend + Local Fallback**

```
┌─────────────────┐
│   Cloud (AWS/   │
│   Azure/GCP)    │
│                 │
│  ┌───────────┐  │
│  │ Backend   │  │
│  │ (FastAPI) │  │
│  │ + OpenAI  │  │
│  │ + Pinecone│  │
│  └───────────┘  │
└────────┬────────┘
         │
         │ Internet (Primary)
         │
┌────────▼────────┐
│  Jetson Nano    │
│                 │
│  ┌───────────┐  │
│  │ Frontend  │  │
│  │ (React)   │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │ Ollama    │  │
│  │ (Offline) │  │
│  └───────────┘  │
│                 │
│  Fallback Mode  │
│  (Offline)      │
└─────────────────┘
```

**Pros:**
- ✅ Best of both worlds
- ✅ Works offline (fallback)
- ✅ Cloud features when online
- ✅ Lower latency for UI

**Cons:**
- ⚠️ More complex setup
- ⚠️ Need to manage both

---

### Option 3: Edge-First with Cloud Sync
**Jetson Nano Primary, Cloud for Sync/Backup**

```
┌─────────────────┐
│   Cloud (AWS/   │
│   Azure/GCP)    │
│                 │
│  ┌───────────┐  │
│  │ Sync/     │  │
│  │ Backup    │  │
│  │ Service   │  │
│  └───────────┘  │
└────────┬────────┘
         │
         │ Periodic Sync
         │
┌────────▼────────┐
│  Jetson Nano    │
│  (Primary)      │
│                 │
│  Full Stack     │
│  + Ollama       │
│  + Offline Mode │
└─────────────────┘
```

**Pros:**
- ✅ Fully offline capable
- ✅ Low latency
- ✅ No cloud dependency

**Cons:**
- ❌ Limited scalability
- ❌ Manual updates

---

## 🚀 Option 1: Full Cloud Deployment

### Step 1: Deploy Backend to Cloud

#### AWS (EC2/Elastic Beanstalk)

**Using EC2:**
```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv nginx git

# 4. Clone repository
git clone https://github.com/mrxvision97/Preventive_legal_AID.git
cd Preventive_legal_AID/backend

# 5. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configure .env
nano .env
# Set:
# - OPENAI_API_KEY=your_key
# - PINECONE_API_KEY=your_key
# - REDIS_HOST=your-redis-endpoint
# - HOST=0.0.0.0
# - PORT=8000

# 7. Install and configure Gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# 8. Set up systemd service
sudo nano /etc/systemd/system/vu-legal-aid.service
```

**Service file:**
```ini
[Unit]
Description=VU Legal AID Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Preventive_legal_AID/backend
Environment="PATH=/home/ubuntu/Preventive_legal_AID/backend/venv/bin"
ExecStart=/home/ubuntu/Preventive_legal_AID/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable vu-legal-aid
sudo systemctl start vu-legal-aid
```

**Using Elastic Beanstalk:**
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB
cd backend
eb init -p python-3.11 vu-legal-aid --region us-east-1

# Create environment
eb create vu-legal-aid-env

# Deploy
eb deploy
```

#### Azure (App Service)

```bash
# 1. Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 2. Login
az login

# 3. Create resource group
az group create --name vu-legal-aid-rg --location eastus

# 4. Create App Service plan
az appservice plan create --name vu-legal-aid-plan --resource-group vu-legal-aid-rg --sku B1 --is-linux

# 5. Create web app
az webapp create --resource-group vu-legal-aid-rg --plan vu-legal-aid-plan --name vu-legal-aid --runtime "PYTHON:3.11"

# 6. Configure environment variables
az webapp config appsettings set --resource-group vu-legal-aid-rg --name vu-legal-aid --settings \
  OPENAI_API_KEY="your_key" \
  PINECONE_API_KEY="your_key" \
  REDIS_HOST="your-redis"

# 7. Deploy from Git
az webapp deployment source config --name vu-legal-aid --resource-group vu-legal-aid-rg --repo-url https://github.com/mrxvision97/Preventive_legal_AID.git --branch main --manual-integration
```

#### Google Cloud Platform (Cloud Run)

```bash
# 1. Install gcloud CLI
# 2. Create Dockerfile for backend
# 3. Build and deploy

# Create Dockerfile
cat > backend/Dockerfile <<EOF
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080"]
EOF

# Build and deploy
gcloud builds submit --tag gcr.io/your-project/vu-legal-aid
gcloud run deploy vu-legal-aid --image gcr.io/your-project/vu-legal-aid --platform managed --region us-central1
```

### Step 2: Deploy Frontend to Cloud

#### Option A: Static Hosting (Recommended)

**AWS S3 + CloudFront:**
```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Create S3 bucket
aws s3 mb s3://vu-legal-aid-frontend

# 3. Upload build
aws s3 sync dist/ s3://vu-legal-aid-frontend --delete

# 4. Enable static website hosting
aws s3 website s3://vu-legal-aid-frontend --index-document index.html

# 5. Create CloudFront distribution
aws cloudfront create-distribution --origin-domain-name vu-legal-aid-frontend.s3.amazonaws.com
```

**Netlify/Vercel:**
```bash
# Install CLI
npm install -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod

# Or connect GitHub repo for auto-deploy
```

#### Option B: Same Server (Nginx)

```bash
# On your backend server
cd frontend
npm run build

# Configure Nginx
sudo nano /etc/nginx/sites-available/vu-legal-aid
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /home/ubuntu/Preventive_legal_AID/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/vu-legal-aid /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 3: Configure Jetson Nano as Client

```bash
# On Jetson Nano - Set up kiosk mode browser

# 1. Install Chromium
sudo apt install -y chromium-browser

# 2. Create kiosk script
nano ~/start-kiosk.sh
```

**Kiosk script:**
```bash
#!/bin/bash
# Start browser in kiosk mode pointing to cloud URL

CHROMIUM_FLAGS="--kiosk --noerrdialogs --disable-infobars --autoplay-policy=no-user-gesture-required"
CLOUD_URL="https://your-cloud-domain.com"

chromium-browser $CHROMIUM_FLAGS $CLOUD_URL
```

```bash
chmod +x ~/start-kiosk.sh

# 3. Auto-start on boot
nano ~/.config/autostart/kiosk.desktop
```

**Desktop file:**
```ini
[Desktop Entry]
Type=Application
Name=Legal AID Kiosk
Exec=/home/jetson/start-kiosk.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

---

## 🔄 Option 2: Hybrid Architecture (Recommended)

### Architecture Overview

- **Cloud**: Backend with OpenAI, Pinecone, Redis
- **Jetson Nano**: Frontend + Ollama (offline fallback)

### Step 1: Deploy Backend to Cloud

Follow **Option 1: Step 1** to deploy backend to cloud.

**Important**: Configure backend to allow CORS from Jetson Nano IP:
```python
# In backend/app/core/config.py
ALLOWED_ORIGINS=http://localhost:3000,http://jetson-nano-ip:3000,https://your-cloud-domain.com
```

### Step 2: Configure Jetson Nano for Hybrid Mode

```bash
# On Jetson Nano

# 1. Set up frontend
cd ~/Preventive_legal_AID/frontend
npm install
npm run build

# 2. Create .env file
nano .env
```

**Frontend .env:**
```bash
# Primary: Cloud backend
VITE_API_URL=https://your-cloud-backend.com

# Fallback: Local backend (if cloud unavailable)
VITE_FALLBACK_API_URL=http://localhost:8000

# Enable offline mode detection
VITE_ENABLE_OFFLINE_MODE=true
```

### Step 3: Update Frontend for Hybrid Mode

Create a connection manager that switches between cloud and local:

```typescript
// frontend/src/lib/apiClient.ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const FALLBACK_API_URL = import.meta.env.VITE_FALLBACK_API_URL || 'http://localhost:8000';

let currentApiUrl = API_URL;

export async function checkCloudConnection(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`, { 
      method: 'GET',
      signal: AbortSignal.timeout(3000) // 3 second timeout
    });
    return response.ok;
  } catch {
    return false;
  }
}

export function getApiUrl(): string {
  return currentApiUrl;
}

export async function switchToFallback() {
  currentApiUrl = FALLBACK_API_URL;
  console.log('Switched to local backend (offline mode)');
}

// Auto-detect on app start
checkCloudConnection().then(connected => {
  if (!connected) {
    switchToFallback();
  }
});
```

### Step 4: Set Up Local Backend on Jetson Nano (Fallback)

```bash
# On Jetson Nano

# 1. Set up backend (offline mode)
cd ~/Preventive_legal_AID/backend
source venv/bin/activate

# 2. Configure .env for offline mode
nano .env
```

**Backend .env (Jetson Nano):**
```bash
# Offline mode configuration
USE_OFFLINE_MODE=true
FORCE_EDGE_MODE=true
OLLAMA_MODEL=qwen:0.5b
OLLAMA_BASE_URL=http://localhost:11434

# Server
HOST=0.0.0.0
PORT=8000

# CORS - allow from frontend
ALLOWED_ORIGINS=http://localhost:3000,http://jetson-nano-ip:3000
```

### Step 5: Create Startup Script

```bash
# On Jetson Nano
nano ~/start-hybrid.sh
```

**Startup script:**
```bash
#!/bin/bash

# Start Ollama (if not running)
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve > /dev/null 2>&1 &
    sleep 5
fi

# Start local backend (fallback)
cd ~/Preventive_legal_AID/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &

# Start frontend
cd ~/Preventive_legal_AID/frontend
npm run dev -- --host 0.0.0.0 --port 3000 > /dev/null 2>&1 &

echo "Hybrid mode started!"
echo "Frontend: http://jetson-nano-ip:3000"
echo "Local Backend: http://jetson-nano-ip:8000"
```

```bash
chmod +x ~/start-hybrid.sh
```

---

## 🔧 Configuration for Hybrid Mode

### Backend Configuration (Cloud)

Update `backend/app/core/config.py` to support both cloud and edge:

```python
# Allow CORS from Jetson Nano
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,https://your-cloud-domain.com"
).split(",")

# Add Jetson Nano IP to allowed origins
JETSON_NANO_IP = os.getenv("JETSON_NANO_IP", "")
if JETSON_NANO_IP:
    ALLOWED_ORIGINS.append(f"http://{JETSON_NANO_IP}:3000")
```

### Frontend Configuration

Update API calls to handle fallback:

```typescript
// frontend/src/services/api.ts
import { getApiUrl, checkCloudConnection, switchToFallback } from '@/lib/apiClient';

export async function queryLegalAI(query: string) {
  // Try cloud first
  try {
    const response = await fetch(`${getApiUrl()}/api/v1/public/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
      signal: AbortSignal.timeout(10000) // 10 second timeout
    });
    
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.warn('Cloud backend unavailable, switching to local...');
    await switchToFallback();
    
    // Retry with local backend
    const response = await fetch(`${getApiUrl()}/api/v1/public/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    
    return await response.json();
  }
}
```

---

## 📊 Comparison Table

| Feature | Full Cloud | Hybrid | Edge-Only |
|---------|-----------|--------|-----------|
| **Internet Required** | ✅ Yes | ⚠️ Partial | ❌ No |
| **Offline Capability** | ❌ No | ✅ Yes | ✅ Yes |
| **Latency** | ⚠️ Higher | ✅ Lower | ✅ Lowest |
| **Scalability** | ✅ High | ✅ High | ❌ Limited |
| **Cost** | ⚠️ Higher | ⚠️ Medium | ✅ Low |
| **Complexity** | ✅ Simple | ⚠️ Medium | ✅ Simple |
| **Updates** | ✅ Easy | ⚠️ Medium | ❌ Manual |

---

## 🚀 Recommended Setup

**For Production with Jetson Nano:**

1. **Deploy backend to cloud** (AWS/Azure/GCP)
2. **Deploy frontend to cloud** (S3/Netlify/Vercel)
3. **Set up Jetson Nano** with:
   - Local frontend (can point to cloud backend)
   - Local backend with Ollama (fallback)
   - Auto-switch between cloud and local

**Benefits:**
- ✅ Works online with cloud features
- ✅ Works offline with local Ollama
- ✅ Best user experience
- ✅ Scalable backend

---

## 📝 Next Steps

1. Choose your deployment architecture
2. Set up cloud backend (AWS/Azure/GCP)
3. Configure Jetson Nano for hybrid mode
4. Test online/offline switching
5. Set up monitoring and logging

---

## 🔗 Additional Resources

- **AWS Deployment**: [AWS Documentation](https://aws.amazon.com/documentation/)
- **Azure Deployment**: [Azure App Service](https://docs.microsoft.com/azure/app-service/)
- **GCP Deployment**: [Cloud Run](https://cloud.google.com/run/docs)
- **Jetson Nano Setup**: See `JETSON_NANO_4GB_SETUP.md`

