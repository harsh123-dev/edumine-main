import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from .data_engine import DataEngine

class AnomalyEngine:
    def __init__(self, data_engine: DataEngine):
        self.data_engine = data_engine

    def detect_anomalies(self, contamination: float = 0.05) -> Dict[str, Any]:
        df = self.data_engine.processed_df.copy()
        meta = self.data_engine.column_metadata
        numeric_features = meta.get('numeric_features', []).copy()
        reg_target = meta.get('reg_target')
        if reg_target and reg_target not in numeric_features:
            numeric_features.append(reg_target)

        if len(numeric_features) < 2:
            return {'error': 'Insufficient numeric features for anomaly detection'}

        X_raw = df[numeric_features].fillna(df[numeric_features].median())
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_raw)

        # Isolation Forest
        iso = IsolationForest(contamination=contamination, random_state=42)
        preds = iso.fit_predict(X_scaled) # -1 is anomaly, 1 is normal
        scores = iso.decision_function(X_scaled) # lower means more anomalous

        df['Is_Anomaly'] = preds == -1
        df['Anomaly_Score'] = [round(float(s), 4) for s in scores]

        anomaly_df = df[df['Is_Anomaly']].sort_values(by='Anomaly_Score')

        # Generate intelligent root cause diagnoses
        flagged_students = []
        id_col = meta.get('id_col')
        name_col = meta.get('name_col')
        class_target = meta.get('class_target')

        for _, row in anomaly_df.iterrows():
            s_id = str(row[id_col]) if id_col and id_col in row else 'STU-ANOM'
            s_name = str(row[name_col]) if name_col and name_col in row else s_id
            
            # Diagnose reason
            reasons = []
            att_cols = [c for c in numeric_features if 'attend' in c.lower()]
            study_cols = [c for c in numeric_features if 'study' in c.lower()]
            exam_cols = [c for c in numeric_features if 'exam' in c.lower() or 'final' in c.lower() or 'gpa' in c.lower()]
            mid_cols = [c for c in numeric_features if 'midterm' in c.lower()]
            lms_cols = [c for c in numeric_features if 'lms' in c.lower()]

            att_val = float(row[att_cols[0]]) if att_cols else None
            study_val = float(row[study_cols[0]]) if study_cols else None
            exam_val = float(row[exam_cols[0]]) if exam_cols else None
            mid_val = float(row[mid_cols[0]]) if mid_cols else None
            lms_val = float(row[lms_cols[0]]) if lms_cols else None

            if att_val is not None and exam_val is not None:
                if att_val > 88 and exam_val < 50:
                    reasons.append("High attendance (>88%) coupled with exam failure - suggests test anxiety or passive attendance")
                elif att_val < 60 and exam_val > 85:
                    reasons.append("Chronic absenteeism (<60%) yet distinction marks - independent learner or potential proxy issue")

            if study_val is not None and exam_val is not None:
                if study_val > 22 and exam_val < 55:
                    reasons.append("Excessive reported study hours (>22 hrs/wk) yielding low marks - study strategy inefficiency")

            if mid_val is not None and exam_val is not None:
                if mid_val > 80 and exam_val < 50:
                    reasons.append("Severe mid-semester performance cliff (Midterm >80 dropped to Final <50)")

            if not reasons:
                reasons.append("Multi-dimensional behavioral deviation across attendance, study pace, and performance metrics")

            flagged_students.append({
                'id': s_id,
                'name': s_name,
                'anomaly_score': float(row['Anomaly_Score']),
                'risk_status': str(row[class_target]) if class_target and class_target in row else 'Unknown',
                'primary_diagnosis': reasons[0],
                'attendance': att_val,
                'exam_score': exam_val,
                'study_hours': study_val
            })

        return {
            'total_students_scanned': len(df),
            'anomalies_detected': len(flagged_students),
            'contamination_rate': contamination,
            'flagged_students': flagged_students[:30]
        }
