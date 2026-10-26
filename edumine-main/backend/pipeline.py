from typing import Dict, Any, Optional
from .data_engine import DataEngine, DEFAULT_DATA_PATH
from .eda_engine import EDAEngine
from .association_engine import AssociationEngine
from .clustering_engine import ClusteringEngine
from .classification_engine import ClassificationEngine
from .regression_engine import RegressionEngine
from .anomaly_engine import AnomalyEngine
from .intervention_engine import InterventionEngine

class EduMinePipeline:
    def __init__(self, data_path: Optional[str] = None):
        self.data_engine = DataEngine(data_path or DEFAULT_DATA_PATH)
        self.eda_engine = EDAEngine(self.data_engine)
        self.association_engine = AssociationEngine(self.data_engine)
        self.clustering_engine = ClusteringEngine(self.data_engine)
        self.classification_engine = ClassificationEngine(self.data_engine)
        self.regression_engine = RegressionEngine(self.data_engine)
        self.anomaly_engine = AnomalyEngine(self.data_engine)
        self.intervention_engine = InterventionEngine(self.data_engine, self.classification_engine, self.regression_engine)

    def reload_dataset(self, file_content: Optional[bytes] = None, filename: Optional[str] = None) -> Dict[str, Any]:
        """Reloads dataset or handles custom upload."""
        summary = self.data_engine.load_data(file_content, filename)
        # Reset cached engine states
        self.classification_engine = ClassificationEngine(self.data_engine)
        self.regression_engine = RegressionEngine(self.data_engine)
        self.intervention_engine = InterventionEngine(self.data_engine, self.classification_engine, self.regression_engine)
        return summary

    def reset_default_dataset(self) -> Dict[str, Any]:
        """Resets to default generated sample dataset."""
        self.data_engine = DataEngine(DEFAULT_DATA_PATH)
        self.eda_engine = EDAEngine(self.data_engine)
        self.association_engine = AssociationEngine(self.data_engine)
        self.clustering_engine = ClusteringEngine(self.data_engine)
        self.classification_engine = ClassificationEngine(self.data_engine)
        self.regression_engine = RegressionEngine(self.data_engine)
        self.anomaly_engine = AnomalyEngine(self.data_engine)
        self.intervention_engine = InterventionEngine(self.data_engine, self.classification_engine, self.regression_engine)
        return self.data_engine.get_summary()

    def run_full_pipeline(self) -> Dict[str, Any]:
        """Executes all data mining modules and packages complete analytical state."""
        return {
            'summary': self.data_engine.get_summary(),
            'eda': self.eda_engine.get_eda_data(),
            'association': self.association_engine.mine_rules(),
            'clustering': self.clustering_engine.run_clustering(n_clusters=3),
            'classification': self.classification_engine.evaluate_models(),
            'regression': self.regression_engine.evaluate_models(),
            'anomaly': self.anomaly_engine.detect_anomalies(),
            'interventions': self.intervention_engine.get_at_risk_interventions()
        }
