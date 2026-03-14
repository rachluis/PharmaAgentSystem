"""
Test Dify Chatflow integration with actual cluster data.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from app.services.dify_service import dify_service
from app.database import SessionLocal
from app.models import ClusterResult

async def test_dify_with_cluster():
    """Test Dify service with real cluster data."""
    print("=" * 60)
    print("Testing Dify Chatflow Integration")
    print("=" * 60)
    
    # Get a cluster result from database
    db = SessionLocal()
    try:
        cluster = db.query(ClusterResult).first()
        if not cluster:
            print("❌ No cluster results found in database.")
            print("Please run clustering analysis first.")
            return
        
        print(f"\n✓ Found cluster result: ID={cluster.cluster_id}")
        print(f"  K-value: {cluster.k_value}")
        print(f"  Silhouette Score: {cluster.silhouette_score}")
        
        # Prepare cluster stats
        print("\n" + "-" * 60)
        print("Preparing cluster statistics...")
        cluster_stats_json = dify_service.prepare_cluster_stats(cluster)
        print(f"Cluster stats (first 200 chars):\n{cluster_stats_json[:200]}...")
        
        # Test streaming
        print("\n" + "-" * 60)
        print("Starting Dify stream...")
        print("-" * 60)
        
        full_response = []
        chunk_count = 0
        
        async for chunk in dify_service.stream_chat(
            cluster_stats=cluster_stats_json,
            user_intent="请生成简洁的营销策略建议",
            user_id="test_user"
        ):
            full_response.append(chunk)
            chunk_count += 1
            # Print first few chunks to show streaming works
            if chunk_count <= 5:
                print(f"Chunk {chunk_count}: {chunk[:50]}...")
        
        print("\n" + "-" * 60)
        print(f"✓ Stream completed! Received {chunk_count} chunks")
        print(f"Total response length: {len(''.join(full_response))} characters")
        print("\n" + "=" * 60)
        print("Full Response:")
        print("=" * 60)
        print(''.join(full_response))
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_dify_with_cluster())
