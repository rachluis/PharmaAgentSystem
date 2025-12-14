"""
Dify Service for AI Report Generation.
"""
import requests
import json
import time
from sqlalchemy.orm import Session
from datetime import datetime

from ..config import get_settings
from ..models import AIReport, ClusterResult, Doctor

settings = get_settings()

class DifyService:
    
    def __init__(self):
        self.api_key = settings.dify_api_key
        self.api_url = settings.dify_api_url
        
    def generate_report(self, db: Session, report_id: int):
        """
        Generate report content using Dify API (or fallback to mock).
        This method is intended to be run as a background task.
        
        Args:
            db: Database session
            report_id: ID of the report to generate
        """
        report = db.query(AIReport).filter(AIReport.report_id == report_id).first()
        if not report:
            print(f"Report {report_id} not found")
            return
            
        try:
            # 1. Prepare Context
            context = self._prepare_context(db, report)
            
            # 2. Call Dify API
            if self.api_key and self.api_url:
                content = self._call_dify_api(context, report.report_type)
            else:
                # Fallback to Mock
                print("Dify API key not configured, using mock generation.")
                time.sleep(2) # Simulate delay
                content = self._mock_generation(context, report.report_type)
            
            # 3. Update Report
            report.report_content = content
            report.status = "published"
            report.generation_time = 2.5 # Mock time or calculation
            report.updated_at = datetime.now()
            
            db.commit()
            print(f"Report {report_id} generated successfully.")
            
        except Exception as e:
            print(f"Error generating report {report_id}: {e}")
            report.status = "failed"
            report.report_content = f"Generation failed: {str(e)}"
            db.commit()

    def _prepare_context(self, db: Session, report: AIReport) -> dict:
        """Prepare context data for the AI."""
        context = {}
        
        if report.related_cluster_id:
            cluster = db.query(ClusterResult).filter(ClusterResult.cluster_id == report.related_cluster_id).first()
            if cluster:
                context['cluster_name'] = cluster.cluster_name
                context['kpi_summary'] = cluster.kpi_summary
                context['strategy_focus'] = cluster.strategy_focus
                
        if report.related_npi:
            doctor = db.query(Doctor).filter(Doctor.npi == report.related_npi).first()
            if doctor:
                context['doctor_name'] = f"{doctor.first_name} {doctor.last_name}"
                context['specialty'] = doctor.specialty
                context['rfm'] = {
                    'R': doctor.recency_days,
                    'F': doctor.frequency,
                    'M': doctor.monetary
                }
                
        return context

    def _call_dify_api(self, context: dict, report_type: str) -> str:
        """Call actual Dify API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare inputs based on Dify app configuration
        inputs = {
            "report_type": report_type,
            "context": json.dumps(context, ensure_ascii=False)
        }
        
        payload = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": "pharma-system-user"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/completion-messages",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result.get('answer', 'No answer from AI')
        except Exception as e:
            print(f"Dify API call failed: {e}")
            raise e

    def _mock_generation(self, context: dict, report_type: str) -> str:
        """Mock content generation."""
        if report_type == "cluster_analysis":
            cluster_name = context.get('cluster_name', 'Unknown Cluster')
            kpi = context.get('kpi_summary', {})
            return f"""# 聚类分析报告: {cluster_name}

## 1. 群体概况
本群体主要由**{kpi.get('Top_Specialty', '相关专科')}**医生组成。
- 平均互动频次: **{kpi.get('Avg_F_Count', 0)}** 次
- 平均贡献价值: **${kpi.get('Avg_M_Amount', 0)}**

## 2. 行为特征
该群体表现出较高的学术参与度，对新药临床数据敏感。

## 3. 策略建议
建议采取以便捷数字化渠道为主的沟通方式，辅以关键节点的学术拜访。
"""
        elif report_type == "doctor_profile":
            doc_name = context.get('doctor_name', 'Unknown Doctor')
            rfm = context.get('rfm', {})
            return f"""# 医生画像: {doc_name}

## 1. 基础信息
- 专科: {context.get('specialty', 'Unknown')}
- 价值分类: 高潜力

## 2. 互动历史 (RFM)
- 最近互动: {rfm.get('R', 0)} 天前
- 互动频次: {rfm.get('F', 0)} 次
- 累计价值: ${rfm.get('M', 0)}

## 3. 下一步行动
建议尽快安排线下拜访，跟进最新的学术会议邀请。
"""
        else:
            return "# 通用报告\n\n自动生成的内容..."

dify_service = DifyService()
