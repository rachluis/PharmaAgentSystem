import sqlite3
import json
import os
import sys

db_path = r'e:\PharmaAgentSystem\backend\pharma.db'
out_path = r'e:\PharmaAgentSystem\ai 补充修改\任务6_数据库真实查询与性能指标.txt'

if not os.path.exists(db_path):
    print("Database not found!")
    sys.exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

with open(out_path, 'w', encoding='utf-8') as f:
    f.write("【任务1】读取数据库中的聚类结果\n")
    f.write("=" * 60 + "\n\n")
    
    # SQL-1
    f.write("SQL-1：查看所有聚类结果批次\n")
    f.write("-" * 30 + "\n")
    try:
        cursor.execute('''
        SELECT cluster_id, cluster_name, algorithm,
               silhouette_score, inertia, kpi_summary
        FROM cluster_results
        ORDER BY cluster_id;
        ''')
        rows = cursor.fetchall()
        for row in rows:
            f.write(f"cluster_id: {row['cluster_id']}\n")
            f.write(f"cluster_name: {row['cluster_name']}\n")
            f.write(f"algorithm: {row['algorithm']}\n")
            f.write(f"silhouette_score: {row['silhouette_score']}\n")
            f.write(f"inertia: {row['inertia']}\n")
            f.write(f"kpi_summary: {row['kpi_summary']}\n")
            f.write("-" * 30 + "\n")
    except Exception as e:
        f.write(f"Error executing SQL-1: {e}\n")
    f.write("\n")
    
    # SQL-2
    f.write("SQL-2：查看各群组医生数量分布\n")
    f.write("-" * 30 + "\n")
    try:
        # User's SQL uses rfm_monetary, rfm_frequency; models are monetary, frequency
        cursor.execute('''
        SELECT cluster_id, cluster_label, COUNT(*) as count,
               ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM doctors), 2) as pct,
               ROUND(AVG(monetary), 2) as avg_monetary,
               ROUND(AVG(frequency), 2) as avg_frequency,
               ROUND(AVG(recency_days), 2) as avg_recency
        FROM doctors
        WHERE cluster_id IS NOT NULL
        GROUP BY cluster_id, cluster_label
        ORDER BY cluster_id;
        ''')
        rows = cursor.fetchall()
        f.write(f"{'cluster_id':<12} | {'cluster_label':<25} | {'count':<8} | {'pct(%)':<8} | {'avg_monetary':<15} | {'avg_frequency':<15} | {'avg_recency':<15}\n")
        f.write("-" * 110 + "\n")
        for row in rows:
            f.write(f"{str(row['cluster_id']):<12} | {str(row['cluster_label']):<25} | {str(row['count']):<8} | {str(row['pct']):<8} | {str(row['avg_monetary']):<15} | {str(row['avg_frequency']):<15} | {str(row['avg_recency']):<15}\n")
    except Exception as e:
        f.write(f"Error executing SQL-2: {e}\n")
    f.write("\n")
    
    # SQL-3
    f.write("SQL-3：查看RFM原始分布统计（验证长尾特征）\n")
    f.write("-" * 30 + "\n")
    try:
        cursor.execute('''
        SELECT
          MIN(monetary)    as m_min,
          MAX(monetary)    as m_max,
          AVG(monetary)    as m_mean,
          MIN(frequency)   as f_min,
          MAX(frequency)   as f_max,
          AVG(frequency)   as f_mean,
          COUNT(*)             as total
        FROM doctors;
        ''')
        row = cursor.fetchone()
        if row:
            f.write(f"Monetary Min  : {row['m_min']}\n")
            f.write(f"Monetary Max  : {row['m_max']}\n")
            f.write(f"Monetary Mean : {row['m_mean']}\n")
            f.write(f"Frequency Min : {row['f_min']}\n")
            f.write(f"Frequency Max : {row['f_max']}\n")
            f.write(f"Frequency Mean: {row['f_mean']}\n")
            f.write(f"Total Records : {row['total']}\n")
    except Exception as e:
        f.write(f"Error executing SQL-3: {e}\n")
    f.write("\n")
    
    # SQL-4
    f.write("SQL-4：查看AI报告表中的性能数据\n")
    f.write("-" * 30 + "\n")
    try:
        cursor.execute('''
        SELECT report_id, generation_time, status, created_at
        FROM ai_reports
        ORDER BY created_at DESC
        LIMIT 5;
        ''')
        rows = cursor.fetchall()
        f.write(f"{'report_id':<10} | {'generation_time(s)':<20} | {'status':<15} | {'created_at':<25}\n")
        f.write("-" * 80 + "\n")
        for row in rows:
            f.write(f"{str(row['report_id']):<10} | {str(row['generation_time']):<20} | {str(row['status']):<15} | {str(row['created_at']):<25}\n")
    except Exception as e:
        f.write(f"Error executing SQL-4 (Table might be empty/schema diff): {e}\n")
    f.write("\n")
    
    f.write("【任务2】读取日志或控制台输出\n")
    f.write("=" * 60 + "\n\n")
    
    f.write("查询 cluster_results 表 kpi_summary 内的 clustering_time_seconds：\n")
    try:
        cursor.execute("SELECT cluster_id, kpi_summary FROM cluster_results WHERE kpi_summary IS NOT NULL")
        rows = cursor.fetchall()
        for row in rows:
            try:
                kpi = json.loads(row['kpi_summary'])
                if 'clustering_time_seconds' in kpi:
                    f.write(f"Cluster ID {row['cluster_id']} - clustering_time_seconds: {kpi['clustering_time_seconds']}\n")
                else:
                    f.write(f"Cluster ID {row['cluster_id']} - kpi_summary: {row['kpi_summary']}\n")
            except Exception:
                pass
    except Exception as e:
         f.write(f"Error checking KPIs: {e}\n")
         
    f.write("\n")
    
    f.write("【任务3】读取 Dify 工作流配置\n")
    f.write("=" * 60 + "\n\n")
    f.write("经过全库扫描项目目录（使用 find 命令模式匹配 *.yml, *.yaml, *.json），未发现任何包含 Dify 节点或工作流导出的 DSL/YAML 配置文件。目前系统中是通过 `dify_service.py` 中的 `httpx.AsyncClient` 直接调用了云端的 Dify Chatflow/Workflow API（接口路径 `/chat-messages`），Dify Agent 节点的编排逻辑配置保存在外部 Dify 平台的云端环境内，未保存在本地代码库中。\n")

conn.close()
print("Success. Saved to", out_path)
