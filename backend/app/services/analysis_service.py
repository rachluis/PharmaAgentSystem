"""
Analysis Service for performing K-Means clustering and managing results.
"""
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import json
from datetime import datetime
import traceback

from ..models import Doctor, ClusterResult, AnalysisTask
from ..database import engine

class AnalysisService:
    
    def perform_clustering(self, db: Session, task_id: int):
        """
        Execute K-Means clustering analysis workflow for a specific task.
        
        Args:
            db: Database session
            task_id: ID of the AnalysisTask to execute
            
        Returns:
            dict: Result summary
        """
        task = db.query(AnalysisTask).filter(AnalysisTask.task_id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
            
        try:
            # 1. Update Task Status
            task.status = "running"
            task.started_at = datetime.now()
            task.progress = 10
            db.commit()
            
            # Parse parameters
            params = json.loads(task.parameters) if task.parameters else {}
            k = params.get('k', 5)
            features = params.get('features', ['recency_days', 'frequency', 'monetary'])
            
            # 2. Load Data
            task.progress = 20
            db.commit()
            print(f"Loading data for clustering task {task_id}...")
            
            # Use explicit column selection for performance
            # Note: We use existing RFM columns from Doctor table
            query_cols = [Doctor.npi] + [getattr(Doctor, f) for f in features if hasattr(Doctor, f)]
            query = db.query(*query_cols)
            df = pd.read_sql(query.statement, db.bind)
            
            if df.empty:
                raise ValueError("No doctor data available for clustering")
                
            # 3. Preprocessing
            task.progress = 30
            db.commit()
            
            df_clean = df.copy().dropna()
            
            # Log transform for skewed features (Frequency and Monetary are typically skewed)
            model_features = []
            for f in features:
                if f in ['frequency', 'monetary', 'total_payments', 'avg_payment_amount']:
                    col_name = f"{f}_log"
                    df_clean[col_name] = np.log1p(df_clean[f])
                    model_features.append(col_name)
                else:
                    model_features.append(f)
            
            # Standardization
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(df_clean[model_features])
            
            # 4. K-Means Clustering
            task.progress = 50
            db.commit()
            print(f"Running K-Means with K={k}...")
            
            kmeans = KMeans(
                n_clusters=k, 
                random_state=42, 
                n_init=10,
                max_iter=300
            )
            cluster_labels = kmeans.fit_predict(X_scaled)
            df_clean['cluster_id'] = cluster_labels
            
            # 5. Calculate Metrics
            task.progress = 70
            db.commit()
            
            inertia = kmeans.inertia_
            # Silhouette score is expensive for large datasets, sample if needed
            if len(df_clean) > 10000:
                # Calculate on a random sample for validation speed
                indices = np.random.choice(len(X_scaled), 10000, replace=False)
                silhouette = silhouette_score(X_scaled[indices], cluster_labels[indices])
            else:
                silhouette = silhouette_score(X_scaled, cluster_labels)
                
            # 6. Analyze Clusters and Auto-label
            summary_stats, cluster_labels_map, strategies_map = self._analyze_clusters(
                df_clean, k, features, global_means=df_clean[features].mean()
            )
            
            # 7. Save Result
            task.progress = 80
            db.commit()
            
            # Create ClusterResult
            result = ClusterResult(
                cluster_name=f"{task.task_name} Result",
                task_id=task.task_id,
                algorithm="k-means",
                features_used=json.dumps(features),
                cluster_labels=json.dumps(cluster_labels_map),
                silhouette_score=float(silhouette),
                inertia=float(inertia),
                kpi_summary=json.dumps(summary_stats), # JSON serializable
                visualization_data=self._prepare_viz_data(df_clean, features, k),
                is_active=True
            )
            db.add(result)
            db.flush() # Get result_id
            
            # 8. Update Doctor Records (Batch)
            task.progress = 90
            db.commit()
            print("Updating Doctor records...")
            
            self._batch_update_doctors(db, df_clean[['npi', 'cluster_id']])
            
            # 9. Complete Task
            task.status = "completed"
            task.progress = 100
            task.completed_at = datetime.now()
            task.result_id = result.cluster_id
            
            db.commit()
            return {"task_id": task_id, "cluster_id": result.cluster_id, "status": "completed"}
            
        except Exception as e:
            db.rollback()
            print(f"Clustering Error: {str(e)}")
            traceback.print_exc()
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()
            db.commit()
            raise e

    def _analyze_clusters(self, df, k, features, global_means):
        """Analyze cluster characteristics and generate labels."""
        stats = {}
        labels_map = {}
        strategies_map = {}
        
        # Calculate summary per cluster using original values (not log transformed)
        grouped = df.groupby('cluster_id')[features].mean()
        counts = df['cluster_id'].value_counts()
        
        for i in range(k):
            cluster_stat = grouped.loc[i].to_dict()
            count = int(counts[i])
            percentage = round((count / len(df)) * 100, 2)
            
            stats[str(i)] = {
                "count": count,
                "percentage": percentage,
                "means": {k: float(v) for k, v in cluster_stat.items()}
            }
            
            # Heuristic Labeling
            labels_map[str(i)] = self._generate_label(cluster_stat, global_means)
            
            # Simple Strategy Rule
            strategies_map[str(i)] = self._generate_strategy_rule(cluster_stat, global_means)
            
        return stats, labels_map, strategies_map

    def _generate_label(self, cluster_means, global_means):
        """Generate a short human-readable label for the cluster."""
        # This assumes we have RFM features. Update logic if different features used.
        m = cluster_means.get('monetary', 0)
        f = cluster_means.get('frequency', 0)
        gm = global_means.get('monetary', 1)
        gf = global_means.get('frequency', 1)
        
        if m > gm * 2:
            return "核心高价值 (VIP)"
        elif m > gm * 1.2:
            return "成长型客户"
        elif f < gf * 0.5:
            return "低活跃客户"
        else:
            return "普通客户"

    def _generate_strategy_rule(self, cluster_means, global_means):
        """Generate simple rule-based strategy."""
        label = self._generate_label(cluster_means, global_means)
        if "VIP" in label:
            return "重点维护：提供专属学术支持和会议邀请。"
        elif "成长" in label:
            return "潜力挖掘：增加拜访频率，介绍新产品。"
        elif "低活跃" in label:
            return "激活策略：调研未处方原因，尝试低门槛活动。"
        else:
            return "常规跟进：保持数字化触达。"

    def _prepare_viz_data(self, df, features, k):
        """Prepare simplified data for frontend charts (e.g. scatter plot)."""
        # Sampling for visualization to keep JSON size manageable
        sample_size = min(len(df), 2000)
        sample = df.sample(n=sample_size, random_state=42)
        
        data = []
        for _, row in sample.iterrows():
            item = {"cluster": int(row['cluster_id'])}
            for f in features:
                item[f] = float(row[f])
            data.append(item)
            
        return json.dumps(data)

    def _batch_update_doctors(self, db: Session, updates_df):
        """Update doctor cluster IDs in batches."""
        # Convert to list of dicts for SQLAlchemy bulk update
        updates = []
        for _, row in updates_df.iterrows():
            updates.append({
                "npi": row['npi'],
                "cluster_id": int(row['cluster_id'])
            })
            
        chunk_size = 5000
        for i in range(0, len(updates), chunk_size):
            db.bulk_update_mappings(Doctor, updates[i:i + chunk_size])
            db.commit()

    def determine_optimal_k(self, db: Session, max_k: int = 10):
        """Compute Inertia for K=1 to max_k to help find Elbow."""
        # Logic similar to clustering but loop K and return inertia list
        pass # To be implemented if creating a dedicated "suggest K" API endpoint

analysis_service = AnalysisService()
