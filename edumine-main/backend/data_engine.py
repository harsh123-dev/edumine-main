import io
import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample_students.csv')

class DataEngine:
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or DEFAULT_DATA_PATH
        self.raw_df: Optional[pd.DataFrame] = None
        self.processed_df: Optional[pd.DataFrame] = None
        self.column_metadata: Dict[str, Any] = {}
        self.load_data()

    def load_data(self, file_content: Optional[bytes] = None, filename: Optional[str] = None) -> Dict[str, Any]:
        """Loads data from file path or raw bytes (for CSV or Excel uploads)."""
        if file_content is not None and filename:
            if filename.endswith('.xlsx') or filename.endswith('.xls'):
                self.raw_df = pd.read_excel(io.BytesIO(file_content))
            else:
                self.raw_df = pd.read_csv(io.BytesIO(file_content))
        else:
            if os.path.exists(self.data_path):
                self.raw_df = pd.read_csv(self.data_path)
            else:
                raise FileNotFoundError(f"Dataset not found at {self.data_path}")

        # Basic sanity cleaning
        self.raw_df.columns = [str(col).strip() for col in self.raw_df.columns]
        self._analyze_columns()
        self._preprocess()
        return self.get_summary()

    def _analyze_columns(self):
        """Intelligently identifies feature types, ID, targets, and categories."""
        df = self.raw_df
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

        # Identify ID/Name columns (Avoid substring match like 'paid')
        id_cols = [c for c in df.columns if c.lower() in ['id', 'student_id', 'studentid', 'roll_no', 'rollno', 'roll', 'matric_no'] or c.lower().endswith('_id') or c.lower().startswith('id_')]
        name_cols = [c for c in categorical_cols if 'name' in c.lower()]
        id_col = id_cols[0] if id_cols else (categorical_cols[0] if categorical_cols and df[categorical_cols[0]].nunique() == len(df) else None)
        name_col = name_cols[0] if name_cols else None

        # Identify Regression Target (Prioritize Final Exam Score, G3, GPA over Midterm/Quiz)
        final_targets = [c for c in numeric_cols if any(k == c.lower() or f"_{k}" in c.lower() or f"{k}_" in c.lower() for k in ['g3', 'final', 'gpa', 'final_exam', 'final_score', 'total_score', 'total_mark'])]
        if not final_targets:
            final_targets = [c for c in numeric_cols if any(k in c.lower() for k in ['final', 'gpa', 'total_score', 'total_mark', 'g3'])]

        if final_targets:
            reg_target = final_targets[0]
        else:
            other_scores = [c for c in numeric_cols if any(k in c.lower() for k in ['score', 'mark', 'grade']) and not any(k in c.lower() for k in ['midterm', 'quiz', 'test', 'assign'])]
            reg_target = other_scores[0] if other_scores else (numeric_cols[-1] if numeric_cols else None)

        # Identify Classification Target (Risk)
        risk_cols = [c for c in df.columns if any(k in c.lower() for k in ['academic_risk', 'risk_status', 'risk', 'dropout', 'pass_fail', 'outcome', 'attrition']) and c.lower() != 'pstatus']
        
        # If no explicit risk column, synthesize Academic_Risk from final grade (e.g. G3 < 10 in 0-20 scale, or score < 50/100)
        if not risk_cols and reg_target:
            max_val = df[reg_target].max()
            threshold = 10 if max_val <= 20 else (2.0 if max_val <= 4.0 else 55)
            df['Academic_Risk'] = df[reg_target].apply(lambda x: 'At-Risk' if x < threshold else 'Safe')
            class_target = 'Academic_Risk'
        else:
            class_target = risk_cols[0] if risk_cols else None

        # Usable features (exclude identifiers, targets, and alternative outcome columns)
        exclude = set(filter(None, [id_col, name_col, class_target, reg_target] + final_targets + risk_cols))
        feature_cols = [c for c in df.columns if c not in exclude]
        numeric_features = [c for c in feature_cols if c in numeric_cols]
        categorical_features = [c for c in feature_cols if c in categorical_cols]

        self.column_metadata = {
            'id_col': id_col,
            'name_col': name_col,
            'class_target': class_target,
            'reg_target': reg_target,
            'numeric_features': numeric_features,
            'categorical_features': categorical_features,
            'all_columns': list(df.columns)
        }

    def _preprocess(self):
        """Cleans missing values and creates scaled feature representations."""
        df = self.raw_df.copy()
        
        # Fill missing values
        for c in self.column_metadata['numeric_features']:
            if df[c].isnull().sum() > 0:
                df[c] = df[c].fillna(df[c].median())
                
        for c in self.column_metadata['categorical_features']:
            if df[c].isnull().sum() > 0:
                df[c] = df[c].fillna(df[c].mode()[0] if not df[c].mode().empty else 'Unknown')

        # Fill targets if missing
        if self.column_metadata['reg_target'] and df[self.column_metadata['reg_target']].isnull().sum() > 0:
            rt = self.column_metadata['reg_target']
            df[rt] = df[rt].fillna(df[rt].median())

        if self.column_metadata['class_target'] and df[self.column_metadata['class_target']].isnull().sum() > 0:
            ct = self.column_metadata['class_target']
            df[ct] = df[ct].fillna(df[ct].mode()[0])

        self.processed_df = df

    def get_summary(self) -> Dict[str, Any]:
        """Returns comprehensive summary of dataset for dashboard header & overview."""
        df = self.processed_df if self.processed_df is not None else self.raw_df
        if df is None:
            return {}

        total_students = len(df)
        num_features = len(self.column_metadata.get('numeric_features', [])) + len(self.column_metadata.get('categorical_features', []))
        
        # Class distribution
        class_target = self.column_metadata.get('class_target')
        class_dist = {}
        risk_count = 0
        risk_pct = 0.0
        if class_target and class_target in df.columns:
            counts = df[class_target].value_counts().to_dict()
            class_dist = {str(k): int(v) for k, v in counts.items()}
            # Find count of risk
            for k, v in class_dist.items():
                if any(x in k.lower() for x in ['at-risk', 'risk', 'fail', 'yes', '1', 'drop']):
                    risk_count = v
                    break
            risk_pct = round((risk_count / total_students) * 100, 1) if total_students > 0 else 0.0

        # Mean performance
        reg_target = self.column_metadata.get('reg_target')
        avg_score = round(float(df[reg_target].mean()), 2) if reg_target and reg_target in df.columns else 0.0

        # Attendance average
        att_cols = [c for c in df.columns if 'attend' in c.lower()]
        avg_attendance = round(float(df[att_cols[0]].mean()), 1) if att_cols else 0.0

        return {
            'total_students': total_students,
            'total_columns': len(df.columns),
            'feature_count': num_features,
            'class_target': class_target,
            'reg_target': reg_target,
            'risk_students_count': risk_count,
            'risk_percentage': risk_pct,
            'average_score': avg_score,
            'average_attendance': avg_attendance,
            'class_distribution': class_dist,
            'columns': self.column_metadata
        }

    def get_preview_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Returns records for the interactive data table."""
        df = self.processed_df if self.processed_df is not None else self.raw_df
        if df is None:
            return []
        # Replace NaN with None for valid JSON serialization
        cleaned = df.head(limit).replace({np.nan: None})
        return cleaned.to_dict(orient='records')
