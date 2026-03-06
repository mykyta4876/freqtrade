"""Test aiodns directly"""
import asyncio
import aiodns

async def test_aiodns():
    resolver = aiodns.DNSResolver()
    try:
        result = await resolver.query('api.mexc.com', 'A')
        print(f"✅ aiodns works! IP: {result.addresses}")
        return True
    except Exception as e:
        print(f"❌ aiodns failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_aiodns())
    exit(0 if result else 1)
