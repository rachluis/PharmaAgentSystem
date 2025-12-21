"""
Dify AI Service for generating marketing strategy reports.
Supports SSE streaming for real-time report generation.
"""
import httpx
import json
from typing import AsyncGenerator, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.config import get_settings
from app.models import AIReport, ClusterResult

settings = get_settings()
logger = logging.getLogger(__name__)


class DifyService:
    """Service for interacting with Dify Chatflow API."""
    
    def __init__(self):
        self.api_key = settings.dify_api_key
        self.api_url = settings.dify_api_url
        self.timeout = 120.0
    
    def _get_headers(self) -> dict:
        """Get HTTP headers for Dify API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def prepare_cluster_stats(self, cluster_result: ClusterResult) -> str:
        """
        Prepare cluster statistics as JSON string for Dify input.
        
        Args:
            cluster_result: ClusterResult database model
            
        Returns:
            JSON string containing cluster statistics
        """
        try:
            kpi_summary = json.loads(cluster_result.kpi_summary) if cluster_result.kpi_summary else {}
            cluster_labels = json.loads(cluster_result.cluster_labels) if cluster_result.cluster_labels else {}
            
            # Calculate K from cluster_labels or kpi_summary
            k_value = len(kpi_summary) if kpi_summary else len(cluster_labels)
            
            stats_dict = {
                "cluster_id": cluster_result.cluster_id,
                "cluster_name": cluster_result.cluster_name or f"Cluster {cluster_result.cluster_id}",
                "k_value": k_value,
                "algorithm": cluster_result.algorithm or "k-means",
                "silhouette_score": float(cluster_result.silhouette_score) if cluster_result.silhouette_score else None,
                "inertia": float(cluster_result.inertia) if cluster_result.inertia else None,
                "clusters": []
            }
            
            # Add individual cluster details
            for cluster_id, stats in kpi_summary.items():
                label = cluster_labels.get(str(cluster_id), f"Cluster {cluster_id}")
                cluster_info = {
                    "cluster_id": cluster_id,
                    "label": label,
                    "size": stats.get('size', 0),
                    "size_percentage": stats.get('size_percentage', 0),
                    "avg_frequency": stats.get('Avg_F_Count', stats.get('avg_frequency', 0)),
                    "avg_monetary": stats.get('Avg_M_Amount', stats.get('avg_monetary', 0)),
                    "avg_recency": stats.get('Avg_R_Days', stats.get('avg_recency', 0))
                }
                stats_dict["clusters"].append(cluster_info)
            
            return json.dumps(stats_dict, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Error preparing cluster stats: {e}")
            return json.dumps({"error": "Failed to prepare cluster statistics"}, ensure_ascii=False)
    
    async def stream_chat(
        self,
        cluster_stats: str,
        user_intent: str = "",
        user_id: str = "default"
    ) -> AsyncGenerator[str, None]:
        """
        Stream AI-generated strategy report using Dify Chatflow API.
        
        Args:
            cluster_stats: JSON string of cluster statistics
            user_intent: User's custom instruction
            user_id: User identifier
            
        Yields:
            Text chunks as they arrive from Dify
        """
        if not self.api_key:
            # Mock mode for development
            logger.warning("No Dify API key configured, using mock mode")
            yield "# AI策略报告 (开发模式)\n\n"
            yield "## 概述\n"
            yield "由于未配置Dify API Key，此报告为模拟内容。\n\n"
            yield f"## 聚类数据\n```json\n{cluster_stats}\n```\n\n"
            yield "## 建议策略\n"
            yield "1. **高价值客户群**: 维护关系，提供专属服务\n"
            yield "2. **潜力客户群**: 增加互动，挖掘需求\n"
            yield "3. **大众客户群**: 通用营销，提高效率\n"
            return
        
        # Construct payload for Dify Chatflow
        # IMPORTANT: Variable names must match Dify workflow start node
        payload = {
            "inputs": {
                "cluster_data": cluster_stats,      # Matches Dify variable name
                "user_focus": user_intent or "请生成详细的营销策略报告"  # Matches Dify variable name
            },
            "query": user_intent or "请根据聚类数据生成营销策略报告",  # Required field, cannot be empty
            "response_mode": "streaming",
            "conversation_id": "",
            "user": user_id
        }
        
        logger.info(f"Calling Dify Chatflow API at {self.api_url}/chat-messages")
        logger.debug(f"Payload inputs: cluster_data={len(cluster_stats)} chars, user_focus={user_intent[:50] if user_intent else 'default'}...")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.api_url}/chat-messages",  # Use chat-messages for Chatflow
                    headers=self._get_headers(),
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = f"Dify API Error {response.status_code}: {error_text.decode()}"
                        logger.error(error_msg)
                        yield f"\n\n[错误: {error_msg}]"
                        return
                    
                    # Parse SSE stream
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                            
                        # Dify SSE format: "data: {...}"
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            
                            # Check for end signal
                            if data_str == "[DONE]":
                                logger.info("Dify stream completed")
                                break
                            
                            try:
                                data = json.loads(data_str)
                                
                                # Extract answer from different event types
                                if "answer" in data:
                                    # For agent_message or message events
                                    yield data["answer"]
                                elif "event" in data:
                                    event_type = data["event"]
                                    
                                    if event_type == "agent_message" and "answer" in data:
                                        yield data["answer"]
                                    elif event_type == "message" and "answer" in data:
                                        yield data["answer"]
                                    elif event_type == "error":
                                        error_msg = data.get("message", "Unknown error")
                                        logger.error(f"Dify error event: {error_msg}")
                                        yield f"\n\n[Dify错误: {error_msg}]"
                                        break
                                        
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse SSE data: {data_str[:100]}... Error: {e}")
                                continue
                                
            except httpx.TimeoutException:
                error_msg = "Request timed out after 120 seconds"
                logger.error(error_msg)
                yield f"\n\n[错误: {error_msg}]"
            except httpx.ConnectError as e:
                error_msg = f"Cannot connect to Dify at {self.api_url}"
                logger.error(f"{error_msg}: {e}")
                yield f"\n\n[连接错误: {error_msg}]"
            except httpx.RequestError as e:
                error_msg = f"Request error: {str(e)}"
                logger.error(error_msg)
                yield f"\n\n[请求错误: {error_msg}]"
            except Exception as e:
                error_msg = f"Unexpected error: {type(e).__name__}: {str(e)}"
                logger.error(error_msg)
                yield f"\n\n[未知错误: {error_msg}]"
    
    def save_report(
        self,
        db: Session,
        title: str,
        content: str,
        cluster_id: int,
        user_id: int,
        user_prompt: Optional[str] = None,
        generation_time: float = 0.0
    ) -> AIReport:
        """
        Save generated report to database.
        
        Args:
            db: Database session
            title: Report title
            content: Full report content (markdown)
            cluster_id: Related cluster ID
            user_id: User who generated the report
            user_prompt: User's custom prompt
            generation_time: Time taken to generate (seconds)
            
        Returns:
            Created AIReport instance
        """
        # Combine user prompt into summary if available
        summary_text = content[:300] if len(content) > 300 else content
        if user_prompt:
            summary_text = f"User Request: {user_prompt}\n\nSummary: {summary_text}"
            
        report = AIReport(
            report_title=title,
            report_type="cluster_strategy",
            report_content=content,
            report_summary=summary_text[:500] if len(summary_text) > 500 else summary_text,
            related_cluster_id=cluster_id,
            generated_by=user_id,
            # user_prompt removed as it is not a column
            generation_time=generation_time,
            status="published",
            created_at=datetime.utcnow()
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        logger.info(f"Saved report {report.report_id} for cluster {cluster_id}")
        return report


# Singleton instance
dify_service = DifyService()
