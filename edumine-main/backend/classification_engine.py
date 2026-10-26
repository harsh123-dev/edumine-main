import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import mutual_info_classif
import warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='sklearn')
from .data_engine import DataEngine

class ClassificationEngine:
    def __init__(self, data_engine: DataEngine):
        self.data_engine = data_engine
        self.best_model: Optional[Pipeline] = None
        self.best_model_name: str = ""
        self.feature_names: List[str] = []
        self.target_encoder: Dict[str, int] = {}
        self.preprocessor: Optional[ColumnTransformer] = None

    def evaluate_models(self) -> Dict[str, Any]:
        df = self.data_engine.processed_df.copy()
        meta = self.data_engine.column_metadata
        class_target = meta.get('class_target')

        if not class_target or class_target not in df.columns:
            return {'error': 'No academic risk classification target found in dataset'}

        numeric_features = meta.get('numeric_features', [])
        categorical_features = meta.get('categorical_features', [])
        feature_cols = numeric_features + categorical_features

        if not feature_cols:
            return {'error': 'No input features available for classification'}

        # Prepare labels
        y_raw = df[class_target].astype(str)
        # Determine positive class (At-Risk)
        unique_classes = sorted(y_raw.unique())
        if len(unique_classes) < 2:
            return {'error': 'Classification target must contain at least 2 distinct classes'}

        # Map to binary (1 = At-Risk / Positive, 0 = Safe / Negative)
        pos_class = next((c for c in unique_classes if any(w in c.lower() for w in ['risk', 'fail', '1', 'yes'])), unique_classes[0])
        neg_class = [c for c in unique_classes if c != pos_class][0]

        y = (y_raw == pos_class).astype(int)
        self.target_encoder = {'positive': pos_class, 'negative': neg_class}

        X = df[feature_cols]

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

        # Preprocessing pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
            ]
        )
        self.preprocessor = preprocessor

        # Define candidate classifiers
        candidate_models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'Support Vector Machine': SVC(probability=True, kernel='rbf', random_state=42),
            'Decision Tree': DecisionTreeClassifier(max_depth=6, random_state=42),
            'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5)
        }

        results = []
        best_f1 = -1.0
        best_roc_data = {}
        best_cm_data = {}

        # Transform X to extract encoded feature names and calculate Mutual Information
        X_train_proc = preprocessor.fit_transform(X_train)
        X_test_proc = preprocessor.transform(X_test)

        cat_encoded_names = []
        if categorical_features:
            cat_encoder = preprocessor.named_transformers_['cat']
            cat_encoded_names = list(cat_encoder.get_feature_names_out(categorical_features))
        all_encoded_features = numeric_features + cat_encoded_names
        self.feature_names = all_encoded_features

        # Feature Importance via Mutual Information
        mi_scores = mutual_info_classif(X_train_proc, y_train, random_state=42)
        feature_importance_list = []
        for name, score in zip(all_encoded_features, mi_scores):
            # Clean up display name
            display_name = name.replace('_', ' ')
            feature_importance_list.append({
                'feature': display_name,
                'importance': round(float(score), 4)
            })
        feature_importance_list.sort(key=lambda x: x['importance'], reverse=True)

        for name, clf in candidate_models.items():
            clf.fit(X_train_proc, y_train)
            y_pred = clf.predict(X_test_proc)
            
            # Predict probabilities if available
            if hasattr(clf, "predict_proba"):
                y_prob = clf.predict_proba(X_test_proc)[:, 1]
            else:
                y_prob = clf.decision_function(X_test_proc)

            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            try:
                auc = roc_auc_score(y_test, y_prob)
            except Exception:
                auc = 0.5

            # 5-Fold Cross Validation
            cv_scores = cross_val_score(clf, X_train_proc, y_train, cv=5, scoring='accuracy')

            model_metrics = {
                'model_name': name,
                'accuracy': round(float(acc) * 100, 2),
                'precision': round(float(prec) * 100, 2),
                'recall': round(float(rec) * 100, 2),
                'f1_score': round(float(f1) * 100, 2),
                'roc_auc': round(float(auc), 3),
                'cv_mean': round(float(cv_scores.mean()) * 100, 2),
                'cv_std': round(float(cv_scores.std()) * 100, 2)
            }
            results.append(model_metrics)

            if f1 > best_f1:
                best_f1 = f1
                self.best_model = clf
                self.best_model_name = name

                # Confusion Matrix
                cm = confusion_matrix(y_test, y_pred)
                best_cm_data = {
                    'tn': int(cm[0, 0]),
                    'fp': int(cm[0, 1]),
                    'fn': int(cm[1, 0]),
                    'tp': int(cm[1, 1]),
                    'matrix': cm.tolist(),
                    'labels': [neg_class, pos_class]
                }

                # ROC Curve points (downsampled for smooth chart)
                fpr, tpr, _ = roc_curve(y_test, y_prob)
                step = max(1, len(fpr) // 25)
                best_roc_data = {
                    'fpr': [round(float(x), 3) for x in fpr[::step]],
                    'tpr': [round(float(x), 3) for x in tpr[::step]],
                    'auc': round(float(auc), 3)
                }

        results.sort(key=lambda x: x['f1_score'], reverse=True)

        return {
            'models_evaluation': results,
            'best_model': self.best_model_name,
            'confusion_matrix': best_cm_data,
            'roc_curve': best_roc_data,
            'feature_importance': feature_importance_list[:12],
            'classes': self.target_encoder
        }

    def predict_single(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predicts academic risk probability and status for a single student."""
        if self.best_model is None or self.preprocessor is None:
            self.evaluate_models()

        meta = self.data_engine.column_metadata
        feature_cols = meta.get('numeric_features', []) + meta.get('categorical_features', [])
        
        # Build DataFrame with input values, filling defaults if missing
        row = {}
        for col in feature_cols:
            if col in input_data and input_data[col] is not None:
                row[col] = input_data[col]
            else:
                # Default from dataset median/mode
                if col in meta.get('numeric_features', []):
                    row[col] = float(self.data_engine.processed_df[col].median())
                else:
                    row[col] = str(self.data_engine.processed_df[col].mode()[0])

        input_df = pd.DataFrame([row])
        X_proc = self.preprocessor.transform(input_df)

        if hasattr(self.best_model, "predict_proba"):
            probs = self.best_model.predict_proba(X_proc)[0]
            risk_prob = float(probs[1])
        else:
            pred = self.best_model.predict(X_proc)[0]
            risk_prob = 1.0 if pred == 1 else 0.0

        is_risk = risk_prob >= 0.45
        status = self.target_encoder.get('positive', 'At-Risk') if is_risk else self.target_encoder.get('negative', 'Safe')

        return {
            'model_used': self.best_model_name,
            'risk_status': status,
            'risk_probability': round(risk_prob * 100, 1),
            'is_at_risk': is_risk,
            'severity': 'Critical' if risk_prob >= 0.75 else ('High' if risk_prob >= 0.50 else ('Moderate' if risk_prob >= 0.30 else 'Low'))
        }
