import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import Ridge, Lasso, LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from .data_engine import DataEngine

class RegressionEngine:
    def __init__(self, data_engine: DataEngine):
        self.data_engine = data_engine
        self.best_model: Optional[Any] = None
        self.best_model_name: str = ""
        self.preprocessor: Optional[ColumnTransformer] = None

    def evaluate_models(self) -> Dict[str, Any]:
        df = self.data_engine.processed_df.copy()
        meta = self.data_engine.column_metadata
        reg_target = meta.get('reg_target')

        if not reg_target or reg_target not in df.columns:
            return {'error': 'No continuous performance target found in dataset'}

        numeric_features = meta.get('numeric_features', [])
        categorical_features = meta.get('categorical_features', [])
        feature_cols = numeric_features + categorical_features

        if not feature_cols:
            return {'error': 'No input features available for regression'}

        y = df[reg_target].astype(float)
        X = df[feature_cols]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
            ]
        )
        self.preprocessor = preprocessor

        X_train_proc = preprocessor.fit_transform(X_train)
        X_test_proc = preprocessor.transform(X_test)

        candidate_regressors = {
            'Gradient Boosting Regressor': GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, random_state=42),
            'Random Forest Regressor': RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42),
            'Ridge Regression': Ridge(alpha=1.0),
            'Lasso Regression': Lasso(alpha=0.1),
            'Support Vector Regressor': SVR(C=1.0, epsilon=0.2)
        }

        results = []
        best_r2 = -float('inf')
        actual_vs_predicted = []
        residuals = []

        for name, reg in candidate_regressors.items():
            reg.fit(X_train_proc, y_train)
            y_pred = reg.predict(X_test_proc)

            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)
            
            # Cross validation
            cv_scores = cross_val_score(reg, X_train_proc, y_train, cv=5, scoring='r2')

            results.append({
                'model_name': name,
                'r2_score': round(float(r2), 4),
                'r2_percentage': round(float(max(0, r2)) * 100, 1),
                'rmse': round(float(rmse), 2),
                'mae': round(float(mae), 2),
                'cv_r2_mean': round(float(cv_scores.mean()), 3),
                'cv_r2_std': round(float(cv_scores.std()), 3)
            })

            if r2 > best_r2:
                best_r2 = r2
                self.best_model = reg
                self.best_model_name = name

                # Sample 40 points for the Actual vs Predicted scatter chart
                y_test_list = list(y_test)
                y_pred_list = list(y_pred)
                sample_indices = np.linspace(0, len(y_test_list) - 1, min(45, len(y_test_list)), dtype=int)
                
                actual_vs_predicted = [
                    {
                        'actual': round(float(y_test_list[i]), 1),
                        'predicted': round(float(y_pred_list[i]), 1),
                        'error': round(float(abs(y_test_list[i] - y_pred_list[i])), 1)
                    }
                    for i in sample_indices
                ]

                # Residual distribution
                errs = y_test - y_pred
                counts, bin_edges = np.histogram(errs, bins=10)
                labels = [f"{round(bin_edges[i], 1)} to {round(bin_edges[i+1], 1)}" for i in range(len(counts))]
                residuals = {
                    'labels': labels,
                    'counts': counts.tolist()
                }

        results.sort(key=lambda x: x['r2_score'], reverse=True)

        return {
            'models_evaluation': results,
            'best_model': self.best_model_name,
            'target_name': reg_target,
            'actual_vs_predicted': actual_vs_predicted,
            'residuals': residuals
        }

    def predict_single(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimates final marks or GPA for a single student."""
        if self.best_model is None or self.preprocessor is None:
            self.evaluate_models()

        meta = self.data_engine.column_metadata
        feature_cols = meta.get('numeric_features', []) + meta.get('categorical_features', [])

        row = {}
        for col in feature_cols:
            if col in input_data and input_data[col] is not None:
                row[col] = input_data[col]
            else:
                if col in meta.get('numeric_features', []):
                    row[col] = float(self.data_engine.processed_df[col].median())
                else:
                    row[col] = str(self.data_engine.processed_df[col].mode()[0])

        input_df = pd.DataFrame([row])
        X_proc = self.preprocessor.transform(input_df)
        pred = self.best_model.predict(X_proc)[0]

        reg_target = meta.get('reg_target', 'Final Score')
        val = round(float(pred), 2)
        
        # Determine grade letter
        if 'gpa' in reg_target.lower():
            grade_letter = 'A' if val >= 3.6 else ('B' if val >= 3.0 else ('C' if val >= 2.4 else ('D' if val >= 2.0 else 'F')))
        else:
            grade_letter = 'O (Outstanding)' if val >= 90 else ('A+ (Excellent)' if val >= 80 else ('A (Very Good)' if val >= 70 else ('B (Good)' if val >= 60 else ('C (Satisfactory)' if val >= 50 else 'F (Fail)'))))

        return {
            'model_used': self.best_model_name,
            'target_name': reg_target,
            'predicted_value': val,
            'grade_letter': grade_letter
        }
