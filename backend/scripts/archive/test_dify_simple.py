"""
Simple test of Dify Chatflow API without database dependency.
"""
import asyncio
import httpx
import json

DIFY_API_KEY = "app-oWu7ZMR2QZ2Gtlc4J1HLpiip"
DIFY_API_URL = "http://localhost/v1"

async def test_dify_chatflow():
    """Test Dify Chatflow with sample data."""
    print("=" * 60)
    print("Testing Dify Chatflow API")
    print("=" * 60)
    print(f"URL: {DIFY_API_URL}/chat-messages")
    print(f"API Key: {DIFY_API_KEY}")
    print()
    
    # Sample cluster statistics
    sample_cluster_stats = json.dumps({
        "k_value": 3,
        "silhouette_score": 0.65,
        "inertia": 12345.67,
        "clusters": [
            {
                "cluster_id": "0",
                "label": "高价值客户",
                "size": 50000,
                "size_percentage": 25.5,
                "avg_frequency": 45.2,
                "avg_monetary": 15000.0,
                "avg_recency": 30
            },
            {
                "cluster_id": "1",
                "label": "潜力客户",
                "size": 80000,
                "size_percentage": 40.8,
                "avg_frequency": 15.3,
                "avg_monetary": 5000.0,
                "avg_recency": 60
            },
            {
                "cluster_id": "2",
                "label": "大众客户",
                "size": 66000,
                "size_percentage": 33.7,
                "avg_frequency": 3.1,
                "avg_monetary": 500.0,
                "avg_recency": 120
            }
        ]
    }, ensure_ascii=False)
    
    print("Sample cluster stats:")
    print(sample_cluster_stats[:200] + "...")
    print()
    
    # Construct payload
    payload = {
        "inputs": {
            "cluster_data": sample_cluster_stats,  # Matches Dify variable name
            "user_focus": "请生成简洁的营销策略建议"  # Matches Dify variable name
        },
        "query": "请根据聚类数据生成营销策略报告",  # Required, cannot be empty
        "response_mode": "streaming",
        "conversation_id": "",
        "user": "test_user"
    }
    
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("-" * 60)
    print("Sending request to Dify Chatflow...")
    print("-" * 60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            async with client.stream(
                "POST",
                f"{DIFY_API_URL}/chat-messages",  # Use chat-messages
                headers=headers,
                json=payload
            ) as response:
                print(f"Status Code: {response.status_code}\n")
                
                if response.status_code != 200:
                    error_body = await response.aread()
                    print(f"❌ Error Response:")
                    print(error_body.decode())
                    return
                
                print("✓ Streaming response:\n")
                print("=" * 60)
                
                chunk_count = 0
                full_response = []
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        
                        if data_str == "[DONE]":
                            print("\n" + "=" * 60)
                            print("✓ Stream completed!")
                            break
                        
                        try:
                            data = json.loads(data_str)
                            
                            # Extract answer
                            if "answer" in data:
                                chunk = data["answer"]
                                full_response.append(chunk)
                                chunk_count += 1
                                print(chunk, end='', flush=True)
                            elif "event" in data:
                                event_type = data["event"]
                                if event_type == "error":
                                    print(f"\n❌ Dify Error: {data.get('message', 'Unknown')}")
                                    break
                        except json.JSONDecodeError:
                            continue
                
                print(f"\n\nTotal chunks received: {chunk_count}")
                print(f"Total length: {len(''.join(full_response))} characters")
                
        except httpx.ConnectError as e:
            print(f"❌ Connection Error: {e}")
            print("Make sure Dify is running on http://localhost")
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dify_chatflow())
