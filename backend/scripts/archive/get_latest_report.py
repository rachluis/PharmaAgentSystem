import sqlite3
import os

db_path = r'e:\PharmaAgentSystem\backend\pharma.db'
out_path = r'e:\PharmaAgentSystem\ai 补充修改\任务7_最新AI策略报告完整原文.md'

if not os.path.exists(db_path):
    print("DB not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
SELECT report_content 
FROM ai_reports 
WHERE status = 'published' 
  AND length(report_content) > 500
ORDER BY created_at DESC 
LIMIT 1;
''')

row = cursor.fetchone()
if row:
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(row[0])
    print("SUCCESS")
else:
    print("NO_REPORT_FOUND")

conn.close()
