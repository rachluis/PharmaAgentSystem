"""
Debug script to see full Dify error response.
"""
import asyncio
import httpx
import json

DIFY_API_KEY = "app-oWu7ZMR2QZ2Gtlc4J1HLpiip"
DIFY_API_URL = "http://localhost/v1"

async def test_both_endpoints():
    """Test both /chat-messages and /workflows/run to see which works."""
    
    sample_data = json.dumps({
        "k_value": 3,
        "clusters": [{"cluster_id": "0", "label": "测试", "size": 1000}]
    }, ensure_ascii=False)
    
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test 1: /workflows/run
    print("=" * 60)
    print("Test 1: POST /workflows/run")
    print("=" * 60)
    
    payload1 = {
        "inputs": {
            "cluster_data": sample_data,
            "user_focus": "测试"
        },
        "response_mode": "blocking",
        "user": "test"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{DIFY_API_URL}/workflows/run",
                headers=headers,
                json=payload1
            )
            print(f"Status: {resp.status_code}")
            print(f"Response:\n{resp.text}\n")
        except Exception as e:
            print(f"Error: {e}\n")
    
    # Test 2: /chat-messages  
    print("=" * 60)
    print("Test 2: POST /chat-messages")
    print("=" * 60)
    
    payload2 = {
        "inputs": {
            "cluster_data": sample_data,
            "user_focus": "测试"
        },
        "query": "",
        "response_mode": "blocking",
        "user": "test"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{DIFY_API_URL}/chat-messages",
                headers=headers,
                json=payload2
            )
            print(f"Status: {resp.status_code}")
            print(f"Response:\n{resp.text}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(test_both_endpoints())
