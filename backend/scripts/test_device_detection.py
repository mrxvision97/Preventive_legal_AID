"""
Test script to verify device detection and model selection
"""
import asyncio
from app.core.edge_optimization import (
    is_edge_device,
    get_optimal_model_size,
    get_optimal_whisper_model,
    optimize_for_edge
)
from app.services.model_service import (
    check_openai_connection,
    check_ollama_connection,
    get_available_model
)

async def test_device_detection():
    """Test device detection and model selection"""
    print("=" * 60)
    print("🔍 Device Detection Test")
    print("=" * 60)
    
    # Test edge device detection
    is_edge = is_edge_device()
    print(f"\n📱 Device Type: {'Edge Device (Jetson Nano)' if is_edge else 'Laptop/Desktop'}")
    
    # Test optimal model selection
    optimal_ollama = get_optimal_model_size()
    optimal_whisper = get_optimal_whisper_model()
    print(f"🎯 Recommended Ollama Model: {optimal_ollama}")
    print(f"🎯 Recommended Whisper Model: {optimal_whisper}")
    
    # Test optimizations
    optimizations = optimize_for_edge()
    print(f"\n⚙️  Optimizations Applied:")
    for key, value in optimizations.items():
        print(f"   - {key}: {value}")
    
    # Test model availability
    print(f"\n🔌 Model Availability:")
    openai_available = await check_openai_connection()
    ollama_available = await check_ollama_connection()
    print(f"   - OpenAI: {'✅ Available' if openai_available else '❌ Not available'}")
    print(f"   - Ollama: {'✅ Available' if ollama_available else '❌ Not available'}")
    
    # Test which model will be used
    try:
        preferred_model = await get_available_model()
        print(f"\n🚀 Preferred Model: {preferred_model}")
        
        if is_edge:
            print("   → Will use Ollama (edge device)")
        else:
            if preferred_model == "openai":
                print("   → Will use OpenAI (best quality on laptop)")
            else:
                print("   → Will use Ollama (OpenAI not available)")
    except Exception as e:
        print(f"\n❌ Error determining preferred model: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Device detection test complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_device_detection())

