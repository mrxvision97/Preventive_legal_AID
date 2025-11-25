# Jetson Nano 4GB - Quick Reference

## 🚀 Quick Start Commands

### Initial Setup (One-time)
```bash
# Run automated setup script
cd backend/scripts
bash setup_jetson_nano_4gb.sh

# Or manual setup (see JETSON_NANO_4GB_SETUP.md)
```

### Daily Usage

#### Start Services
```bash
# Start Ollama (if not running as service)
sudo systemctl start ollama
# Or: ollama serve &

# Start backend
cd ~/Preventive_legal/backend
source ../venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Stop Services
```bash
# Stop backend (Ctrl+C or)
pkill -f uvicorn

# Stop Ollama
sudo systemctl stop ollama
# Or: pkill ollama
```

#### Check Status
```bash
# Check Ollama
curl http://localhost:11434/api/tags
ollama list

# Check backend
curl http://localhost:8000/health

# Check system resources
free -h
sudo tegrastats
```

---

## 📋 Configuration

### Environment Variables (.env)
```bash
# Critical for Jetson Nano 4GB
OLLAMA_MODEL=qwen:0.5b
USE_OFFLINE_MODE=true
FORCE_EDGE_MODE=true
OLLAMA_BASE_URL=http://localhost:11434
```

### Model Management
```bash
# List downloaded models
ollama list

# Download model
ollama pull qwen:0.5b

# Test model
ollama run qwen:0.5b "Hello, test"

# Remove model
ollama rm qwen:0.5b
```

---

## 🔧 Troubleshooting

### Out of Memory
```bash
# Check memory
free -h

# Increase swap (if needed)
sudo fallocate -l 6G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Slow Performance
```bash
# Set max performance
sudo nvpmodel -m 0
sudo jetson_clocks

# Check system load
top
htop
```

### Ollama Not Working
```bash
# Check if running
curl http://localhost:11434/api/tags

# Restart service
sudo systemctl restart ollama

# Check logs
journalctl -u ollama -n 50
```

### Backend Errors
```bash
# Check logs
journalctl -u vu-legal-aid -n 50

# Or if running manually, check terminal output
# Common issues:
# - Virtual environment not activated
# - Dependencies not installed
# - .env file missing or incorrect
```

---

## 📊 Monitoring

### System Resources
```bash
# Memory usage
watch -n 1 free -h

# GPU usage
sudo tegrastats

# CPU usage
top
htop
```

### Application Logs
```bash
# Backend logs (if systemd service)
journalctl -u vu-legal-aid -f

# Ollama logs
journalctl -u ollama -f

# Or check log files
tail -f backend/server.log
```

---

## 🌐 Network Access

### Find IP Address
```bash
hostname -I
# Or
ip addr show
```

### Access Application
```bash
# From browser (replace with your IP)
http://<jetson-ip>:8000/docs

# From another device on same network
http://<jetson-ip>:8000
```

### Firewall (if enabled)
```bash
# Allow ports
sudo ufw allow 8000
sudo ufw allow 3000
sudo ufw allow 11434
```

---

## 🔄 Maintenance

### Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### Update Python Dependencies
```bash
cd ~/Preventive_legal/backend
source ../venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Clean Up
```bash
# Remove unused models
ollama list
ollama rm <model-name>

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

---

## ⚡ Performance Tips

1. **Always use qwen:0.5b** for 4GB RAM
2. **4GB+ swap is essential** - don't skip it
3. **Set max performance mode**: `sudo nvpmodel -m 0 && sudo jetson_clocks`
4. **Close unnecessary apps** during use
5. **Use Ethernet** instead of WiFi for stability
6. **Monitor resources** regularly with `tegrastats`

---

## 📝 Expected Performance

- **Query Processing**: 5-15 seconds
- **Voice Transcription**: 5-15 seconds
- **TTS Generation**: 1-3 seconds
- **Memory Usage**: ~2-3GB (with swap)
- **CPU Usage**: 50-80% during inference

---

## 🆘 Emergency Commands

### Kill All Processes
```bash
# Kill backend
pkill -f uvicorn

# Kill Ollama
pkill ollama

# Kill all Python processes (careful!)
pkill python
```

### Restart Everything
```bash
# Restart Ollama
sudo systemctl restart ollama

# Restart backend (if systemd service)
sudo systemctl restart vu-legal-aid

# Or restart system
sudo reboot
```

### Reset Configuration
```bash
# Backup current .env
cp backend/.env backend/.env.backup

# Create fresh .env
cd backend
# Edit .env with correct settings
```

---

## 📚 Documentation

- **Full Setup Guide**: `JETSON_NANO_4GB_SETUP.md`
- **Offline Setup**: `SETUP_OFFLINE.md`
- **Speed Optimization**: `backend/SPEED_OPTIMIZATION.md`
- **Main README**: `README.md`

---

## 💡 Pro Tips

1. **SSH Access**: Set up SSH for remote access
   ```bash
   # On Jetson Nano
   sudo systemctl enable ssh
   sudo systemctl start ssh
   
   # Connect from another device
   ssh jetson@<jetson-ip>
   ```

2. **Auto-start on Boot**: Services are already configured
   - Ollama: `sudo systemctl enable ollama`
   - Backend: `sudo systemctl enable vu-legal-aid`

3. **Backup Important Files**:
   ```bash
   # Backup .env
   cp backend/.env ~/backup/.env
   
   # Backup models (if needed)
   # Models are stored in ~/.ollama/models
   ```

4. **Use Screen/Tmux** for long-running sessions:
   ```bash
   # Install screen
   sudo apt install screen
   
   # Start session
   screen -S backend
   # Run your commands
   # Detach: Ctrl+A, then D
   # Reattach: screen -r backend
   ```

---

**Quick Help**: For detailed instructions, see `JETSON_NANO_4GB_SETUP.md`

