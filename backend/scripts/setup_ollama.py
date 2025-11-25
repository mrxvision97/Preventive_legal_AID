"""
Setup script to download and configure Ollama models for offline use
Optimized for edge devices like Jetson Nano
"""
import subprocess
import sys
import os

# Recommended models for edge devices (smaller, faster)
EDGE_MODELS = {
    "qwen:0.5b": "Fastest, lowest parameters - BEST for Jetson Nano (recommended)",
    "llama3.2:1b": "Alternative option",
    "llama3.2:3b": "Better quality but slower",
    "qwen2.5:1.5b": "Multilingual support, very efficient",
    "phi3:mini": "Microsoft's efficient model",
}

# Production models (larger, better quality)
PRODUCTION_MODELS = {
    "llama3.2": "Standard quality",
    "mistral": "Alternative option",
    "qwen2.5": "Multilingual",
}

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def download_model(model_name, description=""):
    """Download an Ollama model"""
    print(f"\n📥 Downloading {model_name}...")
    if description:
        print(f"   {description}")
    
    try:
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {model_name} downloaded successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download {model_name}: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def setup_edge_device():
    """Setup for edge devices (Jetson Nano)"""
    print("=" * 60)
    print("🚀 Setting up Ollama for Edge Device (Jetson Nano)")
    print("=" * 60)
    
    if not check_ollama_installed():
        print("\n❌ Ollama is not installed!")
        print("\nInstall Ollama:")
        print("  Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        print("  Windows: Download from https://ollama.ai/download")
        print("  Mac: brew install ollama")
        return False
    
    print("\n✅ Ollama is installed")
    
    # Download recommended edge models
    print("\n📦 Recommended models for Jetson Nano:")
    print("   - qwen:0.5b (~300MB) - FASTEST, lowest parameters (RECOMMENDED)")
    print("   - llama3.2:1b (1.3GB) - Alternative option")
    print("   - llama3.2:3b (2.0GB) - Better quality but slower")
    print("   - qwen2.5:1.5b (1.0GB) - Multilingual support")
    
    choice = input("\nWhich model to download? (1=qwen:0.5b [RECOMMENDED], 2=1b, 3=3b, 4=qwen2.5, 5=all) [1]: ").strip() or "1"
    
    models_to_download = []
    if choice == "1":
        models_to_download = ["qwen:0.5b"]
    elif choice == "2":
        models_to_download = ["llama3.2:1b"]
    elif choice == "3":
        models_to_download = ["llama3.2:3b"]
    elif choice == "4":
        models_to_download = ["qwen2.5:1.5b"]
    elif choice == "5":
        models_to_download = ["qwen:0.5b", "llama3.2:1b", "llama3.2:3b", "qwen2.5:1.5b"]
    else:
        models_to_download = ["qwen:0.5b"]  # Default to fastest
    
    success_count = 0
    for model in models_to_download:
        if download_model(model, EDGE_MODELS.get(model, "")):
            success_count += 1
    
    print(f"\n✅ Setup complete! Downloaded {success_count}/{len(models_to_download)} models")
    print("\n💡 Tip: Set OLLAMA_MODEL in .env to your preferred model")
    
    return success_count > 0

if __name__ == "__main__":
    setup_edge_device()

