# PowerShell script for Windows setup (if running on Windows with Jetson Nano remote)
# Setup script for Jetson Nano - Optimized for edge devices

Write-Host "🚀 Setting up VU Legal AID for Jetson Nano" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if Ollama is installed
$ollamaInstalled = Get-Command ollama -ErrorAction SilentlyContinue

if (-not $ollamaInstalled) {
    Write-Host "📥 Ollama is not installed. Please install manually:" -ForegroundColor Yellow
    Write-Host "   Linux: curl -fsSL https://ollama.ai/install.sh | sh" -ForegroundColor Yellow
    Write-Host "   Or download from: https://ollama.ai/download" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "✅ Ollama is installed" -ForegroundColor Green
}

# Download optimized models
Write-Host ""
Write-Host "📦 Downloading optimized models for Jetson Nano..." -ForegroundColor Cyan
Write-Host "   (This may take 10-30 minutes)" -ForegroundColor Yellow

# Download recommended model (fastest for Jetson Nano)
Write-Host "📥 Downloading qwen:0.5b (RECOMMENDED - fastest, ~300MB)..." -ForegroundColor Cyan
ollama pull qwen:0.5b
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Downloaded qwen:0.5b (~300MB) - FASTEST for Jetson Nano" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to download qwen:0.5b" -ForegroundColor Red
}

# Optional: Download alternative models
$downloadAlt = Read-Host "Download alternative models? (llama3.2:1b, llama3.2:3b) [N]"
if ($downloadAlt -eq "Y" -or $downloadAlt -eq "y") {
    $altModels = @("llama3.2:1b", "llama3.2:3b")
    foreach ($model in $altModels) {
        Write-Host "📥 Downloading $model..." -ForegroundColor Cyan
        ollama pull $model
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Downloaded $model" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to download $model" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host "💡 RECOMMENDED model: qwen:0.5b" -ForegroundColor Cyan
Write-Host "   - Fastest inference" -ForegroundColor Yellow
Write-Host "   - Lowest memory usage (~300MB)" -ForegroundColor Yellow
Write-Host "   - Supports multiple languages" -ForegroundColor Yellow

