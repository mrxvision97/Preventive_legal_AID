"""
Test Ollama connection and model availability
"""
import asyncio
import httpx

async def test_ollama():
    """Test Ollama local connection"""
    base_url = "http://localhost:11434"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check if Ollama is running
            response = await client.get(f"{base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                print("✅ Ollama is running!")
                print(f"Available models: {[m['name'] for m in models]}")
                
                # Test a simple query
                test_response = await client.post(
                    f"{base_url}/api/generate",
                    json={
                        "model": "llama3.2",
                        "prompt": "Say hello in one word",
                        "stream": False
                    },
                    timeout=30.0
                )
                
                if test_response.status_code == 200:
                    result = test_response.json()
                    print(f"✅ Model test successful: {result.get('response', '')[:50]}")
                else:
                    print(f"⚠️ Model test failed: {test_response.text}")
            else:
                print("❌ Ollama is not responding")
                
    except httpx.ConnectError:
        print("❌ Ollama is not running. Start it with: ollama serve")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ollama())

