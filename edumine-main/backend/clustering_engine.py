import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from .data_engine import DataEngine

class ClusteringEngine:
    def __init__(self, data_engine: DataEngine):
        self.data_engine = data_engine

    def run_clustering(self, n_clusters: int = 3, algorithm: str = 'kmeans') -> Dict[str, Any]:
        df = self.data_engine.processed_df.copy()
        meta = self.data_engine.column_metadata
        numeric_features = meta.get('numeric_features', [])

        if len(numeric_features) < 2:
            return {'error': 'Insufficient numeric features for clustering'}

        # Prepare feature matrix
        X_raw = df[numeric_features].fillna(df[numeric_features].median())
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_raw)

        # Elbow analysis (SSE & Silhouette for k=2..7)
        elbow_data = []
        for k in range(2, min(8, len(df))):
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km_labels = km.fit_predict(X_scaled)
            sil = silhouette_score(X_scaled, km_labels) if len(np.unique(km_labels)) > 1 else 0
            elbow_data.append({
                'k': k,
                'sse': round(float(km.inertia_), 2),
                'silhouette': round(float(sil), 3)
            })

        # Run selected clustering algorithm
        if algorithm == 'hierarchical':
            model = AgglomerativeClustering(n_clusters=n_clusters)
            labels = model.fit_predict(X_scaled)
        elif algorithm == 'dbscan':
            model = DBSCAN(eps=1.5, min_samples=5)
            labels = model.fit_predict(X_scaled)
        else: # default kmeans
            model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = model.fit_predict(X_scaled)

        df['Cluster'] = labels
        unique_labels = sorted(list(np.unique(labels)))

        # PCA 2D Projection for interactive scatter visualization
        pca = PCA(n_components=2, random_state=42)
        coords = pca.fit_transform(X_scaled)
        variance_ratio = [round(float(v) * 100, 1) for v in pca.explained_variance_ratio_]

        # Overall Silhouette for chosen model
        current_sil = round(float(silhouette_score(X_scaled, labels)), 3) if len(unique_labels) > 1 else 0.0

        # Cluster Profiling & Persona Generation
        personas = []
        cluster_palette = ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4']
        
        # Identify key columns
        class_target = meta.get('class_target')
        reg_target = meta.get('reg_target')

        for idx, c_id in enumerate(unique_labels):
            c_df = df[df['Cluster'] == c_id]
            size = len(c_df)
            size_pct = round((size / len(df)) * 100, 1)

            # Profile averages
            avg_stats = {}
            for col in numeric_features:
                avg_stats[col] = round(float(c_df[col].mean()), 1)

            # Risk %
            risk_pct = 0.0
            if class_target and class_target in c_df.columns:
                risks = c_df[class_target].astype(str).str.lower()
                risk_count = risks.apply(lambda x: any(w in x for w in ['risk', 'fail', '1', 'yes'])).sum()
                risk_pct = round((risk_count / size) * 100, 1) if size > 0 else 0.0

            # Target score
            avg_score = round(float(c_df[reg_target].mean()), 1) if reg_target and reg_target in c_df.columns else 0.0

            # Determine Persona Label & Action
            if risk_pct >= 50.0 or (avg_score > 0 and avg_score < 60):
                title = "At-Risk / Disengaged Cohort"
                tone = "danger"
                action = "Mandatory academic counseling, attendance monitoring, and targeted assignment catch-up clinics."
            elif avg_score >= 80 or risk_pct <= 5.0:
                title = "High-Flying Achievers"
                tone = "success"
                action = "Peer tutoring mentorship opportunities and advanced honours/capstone projects."
            elif risk_pct > 20:
                title = "Vulnerable / Struggling Students"
                tone = "warning"
                action = "Weekly progress checkpoints, study group matching, and supplementary practice problems."
            else:
                title = "Consistent Moderate Performers"
                tone = "info"
                action = "Regular feedback loops and incentive programs to boost grades towards distinction."

            personas.append({
                'cluster_id': int(c_id),
                'title': f"Cluster {c_id}: {title}" if c_id >= 0 else "Outliers / Noise",
                'color': cluster_palette[idx % len(cluster_palette)] if c_id >= 0 else '#64748b',
                'size': size,
                'percentage': size_pct,
                'avg_score': avg_score,
                'risk_percentage': risk_pct,
                'tone': tone,
                'recommended_action': action,
                'attributes': avg_stats
            })

        # Prepare scatter plot points
        scatter_points = []
        id_col = meta.get('id_col')
        name_col = meta.get('name_col')

        for i, row in df.iterrows():
            c_id = int(row['Cluster'])
            s_id = str(row[id_col]) if id_col and id_col in row else f"STU-{i+1}"
            s_name = str(row[name_col]) if name_col and name_col in row else s_id
            
            scatter_points.append({
                'x': round(float(coords[i, 0]), 2),
                'y': round(float(coords[i, 1]), 2),
                'cluster': c_id,
                'id': s_id,
                'name': s_name,
                'risk': str(row[class_target]) if class_target and class_target in row else 'N/A',
                'score': round(float(row[reg_target]), 1) if reg_target and reg_target in row else None
            })

        return {
            'n_clusters': n_clusters,
            'algorithm': algorithm,
            'silhouette_score': current_sil,
            'pca_variance': variance_ratio,
            'elbow_data': elbow_data,
            'personas': personas,
            'points': scatter_points
        }
