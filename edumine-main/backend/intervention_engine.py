import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .data_engine import DataEngine
from .classification_engine import ClassificationEngine
from .regression_engine import RegressionEngine

class InterventionEngine:
    def __init__(self, data_engine: DataEngine, clf_engine: ClassificationEngine, reg_engine: RegressionEngine):
        self.data_engine = data_engine
        self.clf_engine = clf_engine
        self.reg_engine = reg_engine

    def get_at_risk_interventions(self, limit: int = 15) -> List[Dict[str, Any]]:
        df = self.data_engine.processed_df.copy()
        meta = self.data_engine.column_metadata
        class_target = meta.get('class_target')
        reg_target = meta.get('reg_target')
        id_col = meta.get('id_col')
        name_col = meta.get('name_col')

        if df is None or df.empty:
            return []

        # Filter at risk or low score students
        if class_target and class_target in df.columns:
            at_risk_df = df[df[class_target].astype(str).str.lower().str.contains('risk|fail|1|yes')].copy()
        elif reg_target and reg_target in df.columns:
            at_risk_df = df[df[reg_target] < 60].copy()
        else:
            at_risk_df = df.head(limit).copy()

        if reg_target and reg_target in at_risk_df.columns:
            at_risk_df = at_risk_df.sort_values(by=reg_target, ascending=True)

        interventions = []
        for _, row in at_risk_df.head(limit).iterrows():
            s_id = str(row[id_col]) if id_col and id_col in row else 'STU-RISK'
            s_name = str(row[name_col]) if name_col and name_col in row else s_id
            score = round(float(row[reg_target]), 1) if reg_target and reg_target in row else None

            # Find specific bottlenecks
            actions = []
            att_cols = [c for c in df.columns if 'attend' in c.lower()]
            assign_cols = [c for c in df.columns if 'assign' in c.lower()]
            study_cols = [c for c in df.columns if 'study' in c.lower()]
            mid_cols = [c for c in df.columns if 'midterm' in c.lower()]

            att_val = float(row[att_cols[0]]) if att_cols else 100
            assign_val = float(row[assign_cols[0]]) if assign_cols else 100
            study_val = float(row[study_cols[0]]) if study_cols else 20
            mid_val = float(row[mid_cols[0]]) if mid_cols else 100

            if att_val < 72.0:
                actions.append(f"Issue attendance notice ({att_val}%) and schedule mandatory advisor check-in")
            if assign_val < 65.0:
                actions.append(f"Enroll in homework coaching clinic; assignment completion currently at {assign_val}%")
            if mid_val < 55.0:
                actions.append(f"Provide diagnostic review of midterm exam gap ({mid_val}/100)")
            if study_val < 8.0:
                actions.append(f"Assign peer study buddy to increase self-study time from {study_val} hrs/wk to target 14 hrs/wk")

            if not actions:
                actions.append("Conduct comprehensive 1-on-1 academic counseling and continuous progress tracking")

            urgency = 'CRITICAL' if (score and score < 50) or att_val < 65 else 'HIGH'

            interventions.append({
                'id': s_id,
                'name': s_name,
                'current_score': score,
                'attendance': att_val,
                'urgency': urgency,
                'recommended_interventions': actions
            })

        return interventions

    def simulate_what_if(self, baseline: Dict[str, Any], adjustments: Dict[str, Any]) -> Dict[str, Any]:
        """Runs what-if simulation comparing baseline vs adjusted student attributes."""
        # 1. Base prediction
        base_clf = self.clf_engine.predict_single(baseline)
        base_reg = self.reg_engine.predict_single(baseline)

        # 2. Adjusted student
        improved = baseline.copy()
        improved.update(adjustments)

        imp_clf = self.clf_engine.predict_single(improved)
        imp_reg = self.reg_engine.predict_single(improved)

        # Deltas
        risk_reduction = round(base_clf['risk_probability'] - imp_clf['risk_probability'], 1)
        score_gain = round(imp_reg['predicted_value'] - base_reg['predicted_value'], 1)

        return {
            'baseline': {
                'risk_probability': base_clf['risk_probability'],
                'risk_status': base_clf['risk_status'],
                'predicted_score': base_reg['predicted_value'],
                'grade_letter': base_reg['grade_letter']
            },
            'adjusted': {
                'risk_probability': imp_clf['risk_probability'],
                'risk_status': imp_clf['risk_status'],
                'predicted_score': imp_reg['predicted_value'],
                'grade_letter': imp_reg['grade_letter']
            },
            'impact': {
                'risk_reduction_pct': risk_reduction,
                'score_increase': score_gain,
                'summary': f"Risk reduced by {abs(risk_reduction)}% and estimated grade improved by {score_gain} marks."
            }
        }
