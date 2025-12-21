"""
Test script to verify Dify Workflow API connection.
"""
import httpx
import asyncio

DIFY_API_KEY = "app-oWu7ZMR2QZ2Gtlc4J1HLpiip"
DIFY_API_URL = "http://localhost/v1"

async def test_workflow():
    print(f"Testing Dify Workflow API...")
    print(f"URL: {DIFY_API_URL}/workflows/run")
    print(f"API Key: {DIFY_API_KEY}")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # For Workflow apps, the payload uses 'inputs' not 'query'
    payload = {
        "inputs": {
            # Add your workflow input variables here if required
            # "input_text": "测试输入"
        },
        "response_mode": "blocking",
        "user": "test_user"
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print("\nSending request to /workflows/run ...")
            response = await client.post(
                f"{DIFY_API_URL}/workflows/run",
                headers=headers,
                json=payload
            )
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response Body:")
            print(response.text)
            
            if response.status_code == 200:
                print("\n✅ SUCCESS! Dify Workflow API is working!")
            else:
                print(f"\n⚠️ Got status {response.status_code}")
                print("Check if your workflow requires specific input variables.")
                
        except httpx.ConnectError as e:
            print(f"\n❌ Connection Error: {e}")
        except Exception as e:
            print(f"\n❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_workflow())
