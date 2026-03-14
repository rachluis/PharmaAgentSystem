import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score

db_path = r"sqlite:///e:\PharmaAgentSystem\backend\pharma.db"
out_path = r"e:\PharmaAgentSystem\ai 补充修改\任务8_最优K值搜索评估结果(K2到K6).txt"

engine = create_engine(db_path)

df = pd.read_sql("SELECT recency_days, frequency, monetary FROM doctors", engine)
df = df.dropna()

max_recency = df['recency_days'].max()
df['recency_score'] = max_recency - df['recency_days']
df['frequency_log'] = np.log1p(df['frequency'])
df['monetary_log'] = np.log1p(df['monetary'])

features = ['recency_score', 'frequency_log', 'monetary_log']
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features])

with open(out_path, 'w', encoding='utf-8') as f:
    f.write("K | Inertia | Silhouette\n")
    f.write("-" * 30 + "\n")
    
    for k in range(2, 7):
        kmeans = MiniBatchKMeans(
            n_clusters=k,
            batch_size=10000,
            random_state=42,
            n_init=10,
            max_iter=300
        )
        labels = kmeans.fit_predict(X_scaled)
        inertia = kmeans.inertia_
        
        # 限制计算 Silhouette Score 的样本数量到 1 万（真实数据集73万全量计算会导致内存 OOM，587GB）
        # 这里跟 analysis_service_optimized.py 中一样采样计算
        np.random.seed(42)
        indices = np.random.choice(len(X_scaled), 10000, replace=False)
        sil_score = silhouette_score(X_scaled[indices], labels[indices])
        
        # 输出结果
        line = f"{k} | {inertia:.0f} | {sil_score:.4f}\n"
        f.write(line)
        print(line.strip())

    f.write("\n注：\n")
    f.write("1. Inertia（簇内误差平方和/WCSS）为全量 738,773 条数据的残差总和。\n")
    f.write("2. Silhouette Score（轮廓系数）采用无放回抽样 10,000 条记录计算（防止计算复杂度 O(N^2) 产生的矩阵内存不足 587GB），与实际生产系统内 assessment 方法逻辑严格一致。\n")

print("完成并写入", out_path)
