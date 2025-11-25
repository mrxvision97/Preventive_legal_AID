"""
Quick test script for offline mode on laptop
Tests Ollama connection and model availability
"""
import asyncio
import sys
from app.core.config import settings
from app.services.model_service import (
    check_ollama_connection,
    analyze_with_ollama
)
from app.core.edge_optimization import is_edge_device, get_optimal_model_size

async def test_offline():
    """Test offline mode setup"""
    print("=" * 60)
    print("🧪 Testing Offline Mode (Ollama)")
    print("=" * 60)
    
    # Check device type
    is_edge = is_edge_device()
    print(f"\n📱 Device Type: {'Edge Device' if is_edge else 'Laptop/Desktop'}")
    
    # Check Ollama connection
    print("\n🔌 Checking Ollama connection...")
    ollama_available = await check_ollama_connection()
    
    if not ollama_available:
        print("❌ Ollama is not running!")
        print("\n💡 Start Ollama:")
        print("   ollama serve")
        return False
    
    print("✅ Ollama is running")
    
    # Check model
    model_name = settings.OLLAMA_MODEL
    print(f"\n📦 Configured Model: {model_name}")
    print(f"   (Expected: llama3.2:3b)")
    
    # Test query
    print("\n🚀 Testing query analysis...")
    print("   Query: 'What are my rights if my landlord increases rent?'")
    print("   This may take 10-30 seconds...")
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        result = await analyze_with_ollama(
            query_text="What are my rights if my landlord increases rent suddenly?",
            domain="civil",
            user_context={"user_type": "citizen"},
            language="en",
            rag_context=None
        )
        
        elapsed = asyncio.get_event_loop().time() - start_time
        
        print(f"\n✅ Query completed in {elapsed:.2f} seconds")
        print(f"\n📊 Results:")
        print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
        print(f"   Risk Score: {result.get('risk_score', 'N/A')}")
        print(f"   Analysis: {result.get('analysis', 'N/A')[:100]}...")
        print(f"   Lawyer Consultation: {result.get('lawyer_consultation_recommended', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("✅ Offline mode is working correctly!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Query failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check if Ollama is running: ollama serve")
        print("   2. Check if model is downloaded: ollama list")
        print("   3. Verify model name in .env: OLLAMA_MODEL=llama3.2:3b")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_offline())
    sys.exit(0 if success else 1)

