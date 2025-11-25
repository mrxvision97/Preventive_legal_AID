# Frontend Setup for Jetson Nano (Ubuntu 18.04 + Node.js 16)

This guide will help you set up the frontend on Jetson Nano with Ubuntu 18.04 and Node.js 16.

## Prerequisites

- Jetson Nano with Ubuntu 18.04
- Node.js 16.x installed
- npm 8.x or higher

## Step 1: Install Node.js 16 on Jetson Nano

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Node.js 16 (using NodeSource repository)
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should show v16.x.x
npm --version   # Should show 8.x.x or higher
```

## Step 2: Navigate to Frontend Directory

```bash
cd ~/Preventive_legal/frontend
```

## Step 3: Install Dependencies

```bash
# Clean install (removes node_modules and package-lock.json if they exist)
rm -rf node_modules package-lock.json

# Install dependencies (this may take 10-15 minutes on Jetson Nano)
npm install
```

**Note:** If you encounter memory issues during installation, increase swap space:

```bash
# Create 4GB swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make it permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## Step 4: Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```bash
cd ~/Preventive_legal/frontend
nano .env
```

Add the following:

```env
# Backend API URL
REACT_APP_API_URL=http://localhost:8000

# Or if backend is on different machine:
# REACT_APP_API_URL=http://192.168.1.100:8000

# Port for frontend dev server (optional, defaults to 3000)
PORT=3000
```

## Step 5: Start Development Server

```bash
npm start
```

The application will open at `http://localhost:3000` (or the port you specified).

## Step 6: Build for Production

To create an optimized production build:

```bash
npm run build
```

This creates a `build` folder with optimized static files.

## Step 7: Serve Production Build

### Option 1: Using serve (simple)

```bash
# Install serve globally
sudo npm install -g serve

# Serve the build
serve -s build -l 3000
```

### Option 2: Using nginx (recommended for production)

```bash
# Install nginx
sudo apt-get install -y nginx

# Copy build files
sudo cp -r build/* /var/www/html/

# Or configure nginx for the app
sudo nano /etc/nginx/sites-available/preventive-legal
```

Add nginx configuration:

```nginx
server {
    listen 80;
    server_name localhost;

    root /path/to/Preventive_legal/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable and restart nginx:

```bash
sudo ln -s /etc/nginx/sites-available/preventive-legal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Troubleshooting

### Issue: npm install fails with "ENOMEM" or out of memory

**Solution:**
```bash
# Increase swap space (see Step 3)
# Or install with reduced memory usage:
NODE_OPTIONS="--max-old-space-size=2048" npm install
```

### Issue: Build fails with "JavaScript heap out of memory"

**Solution:**
```bash
# Increase Node.js memory limit
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

### Issue: Port 3000 already in use

**Solution:**
```bash
# Use a different port
PORT=3001 npm start
```

### Issue: Module not found errors

**Solution:**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

### Issue: Proxy not working (API calls fail)

**Solution:**
- Check that backend is running on port 8000
- Verify `.env` file has correct `REACT_APP_API_URL`
- Check `setupProxy.js` exists in frontend root
- Restart dev server after changes

## Performance Optimization for Jetson Nano

1. **Reduce build memory usage:**
   ```bash
   NODE_OPTIONS="--max-old-space-size=2048" npm run build
   ```

2. **Use production build in development:**
   ```bash
   npm run build
   serve -s build -l 3000
   ```

3. **Disable source maps in production:**
   Create `.env.production`:
   ```env
   GENERATE_SOURCEMAP=false
   ```

## Differences from Vite

- **Dev server:** Uses `react-scripts start` instead of `vite`
- **Port:** Defaults to 3000 instead of 5173
- **Build:** Uses Webpack instead of Vite's Rollup
- **Hot reload:** Still works but may be slightly slower
- **Proxy:** Uses `setupProxy.js` instead of vite.config.ts

## Verification

After setup, verify everything works:

1. ✅ Frontend starts: `npm start` → opens on port 3000
2. ✅ Backend connection: Check browser console for API calls
3. ✅ Camera access: Click camera icon → should request permissions
4. ✅ Image upload: Upload image → should process with OCR

## Next Steps

1. Set up backend (see `JETSON_NANO_INSTALL.md`)
2. Configure `.env` files for both frontend and backend
3. Test the full application flow
4. Deploy to production using nginx

