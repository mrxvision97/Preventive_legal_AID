"""
Test Redis connection with provided credentials
"""
import asyncio
import redis.asyncio as redis

async def test_redis():
    """Test Redis Labs connection"""
    try:
        r = await redis.Redis(
            host='redis-11431.c305.ap-south-1-1.ec2.cloud.redislabs.com',
            port=11431,
            username="default",
            password="QtdXhZHAhwe11zCjqLOm1UkU8ud9o5qi",
            decode_responses=True,
            ssl=True
        )
        
        # Test connection
        await r.ping()
        print("✅ Redis connection successful!")
        
        # Test set/get
        await r.set('test_key', 'test_value')
        result = await r.get('test_key')
        print(f"✅ Set/Get test: {result}")
        
        # Clean up
        await r.delete('test_key')
        await r.close()
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_redis())

