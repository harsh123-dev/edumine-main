import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .data_engine import DataEngine

class EDAEngine:
    def __init__(self, data_engine: DataEngine):
        self.data_engine = data_engine

    def get_eda_data(self) -> Dict[str, Any]:
        df = self.data_engine.processed_df
        meta = self.data_engine.column_metadata
        if df is None or df.empty:
            return {}

        numeric_cols = meta.get('numeric_features', []).copy()
        if meta.get('reg_target') and meta['reg_target'] not in numeric_cols:
            numeric_cols.append(meta['reg_target'])

        # 1. Descriptive Statistics
        stats_dict = {}
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) > 0:
                stats_dict[col] = {
                    'mean': round(float(series.mean()), 2),
                    'std': round(float(series.std()), 2),
                    'min': round(float(series.min()), 2),
                    'q25': round(float(series.quantile(0.25)), 2),
                    'median': round(float(series.median()), 2),
                    'q75': round(float(series.quantile(0.75)), 2),
                    'max': round(float(series.max()), 2),
                    'skew': round(float(series.skew()), 2)
                }

        # 2. Correlation Matrix
        corr_matrix = {}
        if len(numeric_cols) > 1:
            corr_df = df[numeric_cols].corr().fillna(0)
            corr_matrix = {
                'columns': list(corr_df.columns),
                'values': [[round(float(val), 2) for val in row] for row in corr_df.values]
            }

        # 3. Distributions (Histograms)
        distributions = {}
        for col in numeric_cols[:6]: # top key numeric features
            series = df[col].dropna()
            counts, bin_edges = np.histogram(series, bins=10)
            labels = [f"{round(bin_edges[i], 1)}-{round(bin_edges[i+1], 1)}" for i in range(len(counts))]
            distributions[col] = {
                'labels': labels,
                'counts': counts.tolist()
            }

        # 4. Feature Comparisons by Risk Status
        risk_comparisons = {}
        class_target = meta.get('class_target')
        if class_target and class_target in df.columns:
            grouped = df.groupby(class_target)
            for col in numeric_cols:
                grp_means = grouped[col].mean().to_dict()
                risk_comparisons[col] = {str(k): round(float(v), 2) for k, v in grp_means.items()}

        # 5. Categorical Breakdown
        categorical_dist = {}
        for col in meta.get('categorical_features', [])[:4]:
            counts = df[col].value_counts().head(8).to_dict()
            categorical_dist[col] = {str(k): int(v) for k, v in counts.items()}

        return {
            'statistics': stats_dict,
            'correlation': corr_matrix,
            'distributions': distributions,
            'risk_comparisons': risk_comparisons,
            'categorical_breakdown': categorical_dist
        }
