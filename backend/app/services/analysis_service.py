"""
Analysis Service for performing K-Means clustering and managing results.
"""
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
import json

from ..models import Doctor, ClusterResult
from ..database import engine

class AnalysisService:
    
    def perform_clustering(self, db: Session, k: int = 5, features: list = None):
        """
        Perform K-Means clustering on doctor data and update the database.
        
        Args:
            db: Database session
            k: Number of clusters
            features: List of features to use (default: recency, frequency, monetary)
        
        Returns:
            dict: Summary of the clustering result
        """
        if features is None:
            features = ['recency_days', 'frequency', 'monetary']
            
        # 1. Load Data
        print("Loading data for clustering...")
        query = db.query(Doctor.npi, Doctor.recency_days, Doctor.frequency, Doctor.monetary)
        df = pd.read_sql(query.statement, db.bind)
        
        if df.empty:
            raise ValueError("No doctor data found for clustering")
            
        # 2. Preprocessing
        df_clean = df.copy().dropna()
        
        # Log transform for skewed features
        # Note: We use log1p to handle zeros safely, though ETL should have handled this
        if 'frequency' in features:
            df_clean['frequency_log'] = np.log1p(df_clean['frequency'])
        if 'monetary' in features:
            df_clean['monetary_log'] = np.log1p(df_clean['monetary'])
            
        # Select features for scaling
        # Map original names to transformed names for the model
        model_features = []
        for f in features:
            if f == 'frequency':
                model_features.append('frequency_log')
            elif f == 'monetary':
                model_features.append('monetary_log')
            else:
                model_features.append(f)
                
        # Scale data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_clean[model_features])
        
        # 3. K-Means Clustering
        print(f"Running K-Means with K={k}...")
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        df_clean['cluster_id'] = kmeans.fit_predict(X_scaled)
        
        # 4. Save Results to Database
        
        # 4.1 Update Doctor table (Batch update)
        # Verify if we can do bulk update efficiently
        print("Updating Doctor records with cluster IDs...")
        
        # Prepare data for bulk update
        # We need a list of dicts: [{'npi': '...', 'cluster_id': 0}, ...]
        updates = df_clean[['npi', 'cluster_id']].to_dict('records')
        
        # Using SQLAlchemy Core for bulk update is faster for large datasets
        # However, SQLite limit might be hit with 700k rows
        # Let's use chunked updates
        chunk_size = 10000
        for i in range(0, len(updates), chunk_size):
            chunk = updates[i:i + chunk_size]
            db.bulk_update_mappings(Doctor, chunk)
            db.commit()
            
        # 4.2 Save Cluster Summaries to ClusterResult table
        print("Calculating cluster summaries...")
        
        # Clear existing results
        db.query(ClusterResult).delete()
        
        # Calculate summaries (use original values, not log-transformed)
        summary = df_clean.groupby('cluster_id')[['recency_days', 'frequency', 'monetary']].agg(['mean', 'count'])
        
        # Calculate top specialties for each cluster
        # This requires a separate query or joining with the original df since we dropped other columns from df
        # Let's run a quick SQL query for this
        
        results = []
        global_means = df_clean[['recency_days', 'frequency', 'monetary']].mean()
        
        for cluster_id in summary.index:
            # Stats
            r_mean = summary.loc[cluster_id, ('recency_days', 'mean')]
            f_mean = summary.loc[cluster_id, ('frequency', 'mean')]
            m_mean = summary.loc[cluster_id, ('monetary', 'mean')]
            count = int(summary.loc[cluster_id, ('monetary', 'count')])
            percentage = (count / len(df_clean)) * 100
            
            # Automated Strategy Generation
            strategy = self._generate_strategy(r_mean, f_mean, m_mean, global_means)
            
            # Create Result Object
            result_obj = ClusterResult(
                cluster_id=int(cluster_id),
                cluster_name=f"Cluster {cluster_id}", # Can be updated by AI later
                size_count=count,
                size_percentage=round(percentage, 2),
                kpi_summary={
                    "Avg_R_Days": round(r_mean, 1),
                    "Avg_F_Count": round(f_mean, 1),
                    "Avg_M_Amount": round(m_mean, 2)
                },
                strategy_focus=strategy,
                context_for_llm=f"R={r_mean:.1f}, F={f_mean:.1f}, M=${m_mean:.2f}"
            )
            db.add(result_obj)
            results.append(result_obj)
            
        db.commit()
        print("Clustering complete.")
        
        return {
            "k": k,
            "total_doctors": len(df_clean),
            "clusters": [r.kpi_summary for r in results]
        }
    
    def _generate_strategy(self, r, f, m, global_means):
        """Simple rule-based strategy generation."""
        tags = []
        if m > global_means['monetary'] * 1.5: tags.append("High Value")
        elif m < global_means['monetary'] * 0.6: tags.append("Low Value")
        
        if f > global_means['frequency'] * 1.5: tags.append("High Frequency")
        elif f < global_means['frequency'] * 0.6: tags.append("Low Frequency")
        
        if r < global_means['recency_days'] * 0.8: tags.append("Active")
        elif r > global_means['recency_days'] * 1.2: tags.append("At Risk")
        
        if "High Value" in tags and "Active" in tags:
            return "VIP Maintenance: Invite to exclusive events, prioritize personal visits."
        elif "High Value" in tags and "At Risk" in tags:
            return "Win-Back: Immediate intervention required, offer incentives."
        elif "Low Value" in tags and "Active" in tags:
            return "Growth Potential: Cross-sell new products to increase value."
        else:
             return "General Engagement: Standard digital outreach."

    def generate_ai_strategies(self, db: Session):
        """
        Generate (Mock) AI strategies for all clusters.
        """
        print("Generating AI strategies for clusters...")
        clusters = db.query(ClusterResult).all()
        
        # Calculate global means for comparison context
        # In a real app we might cache this or pass it in
        # For now, we'll re-calculate or approximate
        # Let's assume we can get it from the full dataset if needed
        # Or simpler: just use the rules based on absolute values for the mock
        
        updated_count = 0
        for cluster in clusters:
            # Prepare context
            summary = cluster.kpi_summary
            r = summary.get("Avg_R_Days", 0)
            f = summary.get("Avg_F_Count", 0)
            m = summary.get("Avg_M_Amount", 0)
            
            # Generate Strategy (Mock)
            strategy = self._mock_ai_generate(r, f, m)
            
            # Update Cluster
            cluster.strategy_focus = strategy
            updated_count += 1
            
        db.commit()
        print(f"Updated strategies for {updated_count} clusters.")
        return updated_count

    def _mock_ai_generate(self, r, f, m):
        """
        Mock AI generation based on rules.
        In production, this would call Dify API with a prompt.
        """
        # Simple logical segmentation
        strategies = []
        
        # Value dimension
        if m > 5000:
            value_seg = "High Value (VIP)"
            strategies.append("Inviting to exclusive national conferences.")
            strategies.append("Providing premium academic support and latest trial data.")
        elif m > 500:
            value_seg = "Medium Value"
            strategies.append("Regular product updates via digital channels.")
            strategies.append("Regional seminar invitations.")
        else:
            value_seg = "Low Value"
            strategies.append("Automated email campaigns.")
            strategies.append("General educational content distribution.")
            
        # Frequency dimension
        if f > 20:
            freq_seg = "High Frequency"
            strategies.append("Maintaining relationship with frequent touchpoints.")
        else:
            freq_seg = "Low Frequency"
            strategies.append("Identifying barriers to prescribing.")
            strategies.append("Incentivizing trial usage.")
            
        # Recency dimension
        if r < 60:
            active_seg = "Active"
        elif r < 180:
            active_seg = "Lapsing"
            strategies.append("Re-engagement campaign urgently needed.")
        else:
            active_seg = "Inactive"
            strategies.append("Win-back program with special offers.")
            
        # Construct full strategy text
        strategy_text = f"**Segment**: {value_seg} | {freq_seg} | {active_seg}\n\n**Recommended Actions**:\n"
        for i, action in enumerate(strategies, 1):
            strategy_text += f"{i}. {action}\n"
            
        return strategy_text


analysis_service = AnalysisService()
