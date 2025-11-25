"""
Automatically download and configure models for offline use
Optimized for edge devices
"""
import subprocess
import sys
import asyncio
from app.core.edge_optimization import is_edge_device, get_optimal_model_size

async def download_models_auto():
    """Automatically download optimal models based on device"""
    print("🔍 Detecting device capabilities...")
    
    is_edge = is_edge_device()
    optimal_model = get_optimal_model_size()
    
    print(f"📱 Device Type: {'Edge Device (Jetson Nano)' if is_edge else 'Standard Device'}")
    print(f"🎯 Recommended Model: {optimal_model}")
    
    # Check if Ollama is installed
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError
        print("✅ Ollama is installed")
    except FileNotFoundError:
        print("❌ Ollama is not installed!")
        print("\nInstall Ollama:")
        print("  curl -fsSL https://ollama.ai/install.sh | sh")
        return False
    
    # Download recommended model
    print(f"\n📥 Downloading recommended model: {optimal_model}")
    print("   This may take 5-15 minutes (qwen:0.5b is very small ~300MB)...")
    
    try:
        subprocess.run(
            ["ollama", "pull", optimal_model],
            check=True,
            timeout=1800  # 30 minutes max
        )
        print(f"✅ Successfully downloaded {optimal_model}")
        
        # qwen:0.5b already supports multiple languages, so no need for additional model
        # But offer as optional
        if is_edge and optimal_model == "qwen:0.5b":
            print("\n💡 qwen:0.5b already supports multiple languages (English, Hindi, etc.)")
        
        print("\n✅ Model setup complete!")
        print(f"\n💡 Set in .env: OLLAMA_MODEL={optimal_model}")
        print(f"💡 qwen:0.5b is optimized for Jetson Nano - fastest with lowest parameters!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download model: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(download_models_auto())

