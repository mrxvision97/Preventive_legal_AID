# Frontend Migration from Vite to Create React App

This project has been migrated from Vite to Create React App (CRA) for compatibility with:
- **Node.js 16** (required for Jetson Nano Ubuntu 18.04)
- **Ubuntu 18.04** (Jetson Nano default OS)

## What Changed

### Removed
- ❌ `vite.config.ts` - Vite configuration
- ❌ `tsconfig.node.json` - Vite-specific TypeScript config
- ❌ Vite dependencies

### Added
- ✅ `react-scripts` - CRA build tool (supports Node 16)
- ✅ `setupProxy.js` - API proxy configuration
- ✅ `public/` folder - Static assets directory
- ✅ CRA-compatible `tsconfig.json`
- ✅ Updated `package.json` for CRA

### Modified
- 📝 `index.html` - Updated for CRA (no module scripts)
- 📝 `package.json` - Changed scripts and dependencies
- 📝 `tsconfig.json` - CRA-compatible TypeScript config
- 📝 `tailwind.config.js` - Changed to CommonJS format
- 📝 `postcss.config.js` - Changed to CommonJS format

## Installation on Jetson Nano

```bash
# 1. Install Node.js 16
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# 2. Navigate to frontend
cd ~/Preventive_legal/frontend

# 3. Remove old dependencies
rm -rf node_modules package-lock.json

# 4. Install new dependencies
npm install

# 5. Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# 6. Start development server
npm start
```

## Key Differences

| Feature | Vite | Create React App |
|---------|------|------------------|
| Node.js | 18+ | 16+ ✅ |
| Dev Server | Port 5173 | Port 3000 |
| Build Tool | Rollup | Webpack |
| Hot Reload | Fast | Good |
| Proxy Config | vite.config.ts | setupProxy.js |
| Build Speed | Very Fast | Fast |

## Scripts

- `npm start` - Start development server (port 3000)
- `npm run build` - Create production build
- `npm test` - Run tests
- `npm run eject` - Eject from CRA (not recommended)

## Environment Variables

Create `.env` file in `frontend/` directory:

```env
REACT_APP_API_URL=http://localhost:8000
PORT=3000
GENERATE_SOURCEMAP=false
```

**Note:** All environment variables must start with `REACT_APP_` to be accessible in the app.

## Troubleshooting

### Memory Issues
```bash
# Increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Build with limited memory
NODE_OPTIONS="--max-old-space-size=2048" npm run build
```

### Port Already in Use
```bash
PORT=3001 npm start
```

### Module Not Found
```bash
rm -rf node_modules package-lock.json
npm install
```

## Production Build

```bash
# Build for production
npm run build

# Serve the build
npx serve -s build -l 3000
```

## UI Remains the Same

✅ All UI components work exactly the same  
✅ Tailwind CSS styling unchanged  
✅ React Router navigation unchanged  
✅ All features (camera, OCR, voice) work the same  
✅ No code changes needed in components  

The only change is the build tool - the UI and functionality remain identical!

