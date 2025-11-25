"""
Pre-download Whisper models for offline use
Optimized for edge devices
"""
import whisper
import sys
from app.core.edge_optimization import is_edge_device, get_optimal_whisper_model

def download_whisper_models():
    """Download Whisper models for offline use"""
    print("🔍 Detecting device capabilities...")
    
    is_edge = is_edge_device()
    optimal_model = get_optimal_whisper_model()
    
    print(f"📱 Device Type: {'Edge Device (Jetson Nano)' if is_edge else 'Standard Device'}")
    print(f"🎯 Recommended Whisper Model: {optimal_model}")
    
    models_to_download = [optimal_model]
    
    # For edge devices, also download tiny as backup
    if is_edge and optimal_model != "tiny":
        models_to_download.append("tiny")
    
    print(f"\n📥 Downloading Whisper models: {', '.join(models_to_download)}")
    print("   This may take 5-15 minutes per model...")
    
    for model_size in models_to_download:
        try:
            print(f"\n📦 Downloading {model_size}...")
            whisper.load_model(model_size)
            print(f"✅ {model_size} downloaded and cached")
        except Exception as e:
            print(f"❌ Failed to download {model_size}: {e}")
            if model_size == optimal_model:
                print("⚠️ Recommended model failed, trying tiny as fallback...")
                try:
                    whisper.load_model("tiny")
                    print("✅ tiny model downloaded as fallback")
                except Exception as fallback_error:
                    print(f"❌ Fallback also failed: {fallback_error}")
                    sys.exit(1)
    
    print("\n✅ Whisper models ready for offline use!")
    print(f"💡 System will use '{optimal_model}' model by default")

if __name__ == "__main__":
    download_whisper_models()

