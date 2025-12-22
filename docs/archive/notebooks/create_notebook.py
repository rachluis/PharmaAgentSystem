
import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# Cell 1: Imports
text_1 = """\
# 1. Imports and Setup
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import plotly.express as px
import plotly.graph_objects as go

# Set plot style
sns.set(style="whitegrid")
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial']  # For Chinese characters
plt.rcParams['axes.unicode_minus'] = False

# Add parent dir to path to access app modules if needed
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
print("Libraries imported successfully")\
"""

# Cell 2: Load Data
text_2 = """\
# 2. Load Data from SQLite
# Assuming notebook is running in backend/notebooks/, db is in backend/pharma.db
db_path = '../pharma.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    # Connect to database
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Query RFM data
    query = "SELECT npi, recency_days, frequency, monetary FROM doctors"
    df = pd.read_sql(query, engine)
    
    print(f"Data loaded: {df.shape[0]} doctors")
    print("Head:")
    print(df.head())
    print("\\nStatistics:")
    print(df.describe().round(2))\
"""

# Cell 3: Exploration
text_3 = """\
# 3. Data Exploration & Visualization
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Recency
sns.histplot(df['recency_days'], kde=True, ax=axes[0], color='skyblue')
axes[0].set_title('Recency Distribution')

# Frequency (Log scale often better for visualization due to long tail)
sns.histplot(df['frequency'], kde=True, ax=axes[1], color='orange')
axes[1].set_title('Frequency Distribution')
axes[1].set_xlim(0, df['frequency'].quantile(0.99)) # Show 99% of data

# Monetary
sns.histplot(df['monetary'], kde=True, ax=axes[2], color='green')
axes[2].set_title('Monetary Distribution')
axes[2].set_xlim(0, df['monetary'].quantile(0.99))

plt.tight_layout()
plt.show()

# Skewness check
print("Skewness:")
print(df[['recency_days', 'frequency', 'monetary']].skew())\
"""

# Cell 4: Preprocessing
text_4 = """\
# 4. Preprocessing

# Log Transformation for Skewed Features (frequency and monetary)
# Using log1p to handle any potential 0s safely
df_clean = df.copy()
df_clean['frequency_log'] = np.log1p(df_clean['frequency'])
df_clean['monetary_log'] = np.log1p(df_clean['monetary'])

# Visualize Log-Transformed Distributions
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sns.histplot(df_clean['frequency_log'], kde=True, ax=axes[0], color='orange')
axes[0].set_title('Log-Frequency Distribution')

sns.histplot(df_clean['monetary_log'], kde=True, ax=axes[1], color='green')
axes[1].set_title('Log-Monetary Distribution')
plt.show()

# Standardization (Z-score scaling)
scaler = StandardScaler()
features_to_scale = ['recency_days', 'frequency_log', 'monetary_log']
scaled_features = scaler.fit_transform(df_clean[features_to_scale])

# Create DF for stats checking
df_scaled = pd.DataFrame(scaled_features, columns=features_to_scale)
print("Scaled Data Stats:")
print(df_scaled.describe().round(2))\
"""

# Cell 5: K-Selection
text_5 = """\
# 5. K Selection (Elbow Method & Silhouette Score)

sse = []
silhouette_scores = []
k_range = range(2, 9)

# Use a sample for Silhouette Score calculation to save time (N=15k is sufficient for trend)
sample_size = 15000
if len(df_scaled) > sample_size:
    df_sample = df_scaled.sample(n=sample_size, random_state=42)
else:
    df_sample = df_scaled

print(f"Calculating for K={list(k_range)} using sample size {len(df_sample)}...")

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(df_sample)
    
    # Inertia (SSE)
    sse.append(kmeans.inertia_)
    
    # Silhouette Score
    score = silhouette_score(df_sample, kmeans.labels_)
    silhouette_scores.append(score)
    print(f"K={k}: SSE={kmeans.inertia_:.1f}, Silhouette={score:.4f}")

# Plot Results
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Elbow Plot
axes[0].plot(k_range, sse, marker='o')
axes[0].set_xlabel('Number of Clusters (K)')
axes[0].set_ylabel('SSE (Inertia)')
axes[0].set_title('Elbow Method')

# Silhouette Plot
axes[1].plot(k_range, silhouette_scores, marker='o', color='red')
axes[1].set_xlabel('Number of Clusters (K)')
axes[1].set_ylabel('Silhouette Score')
axes[1].set_title('Silhouette Analysis')

plt.tight_layout()
plt.show()

# Recommendation
best_k = k_range[np.argmax(silhouette_scores)]
print(f"Recommended K based on max Silhouette Score: {best_k}")\
"""

# Cell 6: Clustering
text_6 = """\
# 6. Run K-Means Clustering

# Set K (you can manually override this based on the plots above)
SELECTED_K = best_k  # or manually set e.g., 4

print(f"Running K-Means with K={SELECTED_K} on full dataset...")
kmeans_final = KMeans(n_clusters=SELECTED_K, random_state=42, n_init=10)

# Fit on ALL data
df_clean['cluster'] = kmeans_final.fit_predict(scaled_features)

print("Cluster Counts:")
print(df_clean['cluster'].value_counts().sort_index())\
"""

# Cell 7: Visualization
text_7 = """\
# 7. Visualization

# 7.1 3D Scatter Plot (Sampled)
plot_sample = df_clean.sample(n=min(5000, len(df_clean)), random_state=42)

fig = px.scatter_3d(
    plot_sample, 
    x='recency_days', 
    y='frequency', 
    z='monetary',
    color='cluster',
    title='3D View of Doctor Clusters (RFM)',
    opacity=0.7,
    size_max=10
)
fig.show()

# 7.2 Radar Chart of Center Points
# Calculate means for each cluster
cluster_means = df_clean.groupby('cluster')[['recency_days', 'frequency', 'monetary']].mean()

# Normalize means to 0-1 range for radar chart comparison
min_max_scaler = MinMaxScaler()
radar_data = pd.DataFrame(
    min_max_scaler.fit_transform(cluster_means), 
    columns=cluster_means.columns,
    index=cluster_means.index
)

# Create Radar Plot
categories = list(radar_data.columns)
fig = go.Figure()

for i in radar_data.index:
    fig.add_trace(go.Scatterpolar(
        r=radar_data.loc[i].values,
        theta=categories,
        fill='toself',
        name=f'Cluster {i}'
    ))

fig.update_layout(
  polar=dict(
    radialaxis=dict(
      visible=True,
      range=[0, 1]
    )),
  showlegend=True,
  title="Cluster Center Characteristics (Normalized)"
)
fig.show()\
"""

# Cell 8: Interpretation
text_8 = """\
# 8. Business Interpretation

# Calculate raw stats per cluster
summary_stats = df_clean.groupby('cluster').agg({
    'recency_days': 'mean',
    'frequency': 'mean',
    'monetary': ['mean', 'count']
}).round(2)

print("Cluster Statistics (Raw Means):")
print(summary_stats)

print("\\n--- Automated Interpretation ---")
global_means = df_clean[['recency_days', 'frequency', 'monetary']].mean()

for i in summary_stats.index:
    c_r = summary_stats.loc[i, ('recency_days', 'mean')]
    c_f = summary_stats.loc[i, ('frequency', 'mean')]
    c_m = summary_stats.loc[i, ('monetary', 'mean')]
    count = summary_stats.loc[i, ('monetary', 'count')]
    
    tags = []
    # Logic: Comparative to global mean
    if c_m > global_means['monetary'] * 1.5: tags.append("High Value")
    elif c_m < global_means['monetary'] * 0.6: tags.append("Low Value")
    
    if c_f > global_means['frequency'] * 1.5: tags.append("High Frequency")
    elif c_f < global_means['frequency'] * 0.6: tags.append("Low Frequency")
    
    if c_r < global_means['recency_days'] * 0.8: tags.append("Recent/Active")
    elif c_r > global_means['recency_days'] * 1.2: tags.append("At Risk/Inactive")
    
    desc = ", ".join(tags) if tags else "Average Behavior"
    print(f"Cluster {i} (N={count}): {desc}")\
"""

cells = [
    nbf.v4.new_code_cell(text_1),
    nbf.v4.new_code_cell(text_2),
    nbf.v4.new_code_cell(text_3),
    nbf.v4.new_code_cell(text_4),
    nbf.v4.new_code_cell(text_5),
    nbf.v4.new_code_cell(text_6),
    nbf.v4.new_code_cell(text_7),
    nbf.v4.new_code_cell(text_8)
]

nb['cells'] = cells

with open('clustering_experiment.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook created: clustering_experiment.ipynb")
