import os
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

from .pipeline import EduMinePipeline

app = FastAPI(title="EduMine Data Mining API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = EduMinePipeline()

class SinglePredictionRequest(BaseModel):
    data: Dict[str, Any]

class WhatIfRequest(BaseModel):
    baseline: Dict[str, Any]
    adjustments: Dict[str, Any]

@app.get("/api/summary")
def get_summary():
    return pipeline.data_engine.get_summary()

@app.get("/api/preview")
def get_preview(limit: int = Query(default=100, ge=1, le=500)):
    return {
        'records': pipeline.data_engine.get_preview_data(limit=limit),
        'columns': pipeline.data_engine.column_metadata.get('all_columns', [])
    }

@app.get("/api/eda")
def get_eda():
    return pipeline.eda_engine.get_eda_data()

@app.get("/api/association")
def get_association(
    min_support: float = Query(default=0.08, ge=0.01, le=0.8),
    min_confidence: float = Query(default=0.45, ge=0.1, le=1.0),
    min_lift: float = Query(default=1.1, ge=0.5, le=10.0)
):
    return pipeline.association_engine.mine_rules(
        min_support=min_support,
        min_confidence=min_confidence,
        min_lift=min_lift
    )

@app.get("/api/clustering")
def get_clustering(
    n_clusters: int = Query(default=3, ge=2, le=7),
    algorithm: str = Query(default='kmeans')
):
    return pipeline.clustering_engine.run_clustering(n_clusters=n_clusters, algorithm=algorithm)

@app.get("/api/classification")
def get_classification():
    return pipeline.classification_engine.evaluate_models()

@app.get("/api/regression")
def get_regression():
    return pipeline.regression_engine.evaluate_models()

@app.get("/api/anomalies")
def get_anomalies(contamination: float = Query(default=0.05, ge=0.01, le=0.2)):
    return pipeline.anomaly_engine.detect_anomalies(contamination=contamination)

@app.get("/api/interventions")
def get_interventions(limit: int = Query(default=15, ge=1, le=50)):
    return {
        'interventions': pipeline.intervention_engine.get_at_risk_interventions(limit=limit)
    }

@app.post("/api/predict/single")
def predict_single(req: SinglePredictionRequest):
    risk_pred = pipeline.classification_engine.predict_single(req.data)
    score_pred = pipeline.regression_engine.predict_single(req.data)
    return {
        'risk': risk_pred,
        'performance': score_pred
    }

@app.post("/api/simulate/what-if")
def simulate_what_if(req: WhatIfRequest):
    return pipeline.intervention_engine.simulate_what_if(req.baseline, req.adjustments)

@app.post("/api/dataset/upload")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        content = await file.read()
        summary = pipeline.reload_dataset(file_content=content, filename=file.filename)
        return {
            'status': 'success',
            'filename': file.filename,
            'summary': summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/dataset/reset")
def reset_dataset():
    summary = pipeline.reset_default_dataset()
    return {
        'status': 'success',
        'message': 'Restored default sample dataset',
        'summary': summary
    }

@app.get("/api/pipeline/run-all")
def run_all():
    return pipeline.run_full_pipeline()

# Frontend static serving
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "EduMine API running. Frontend index.html not yet initialized."}
