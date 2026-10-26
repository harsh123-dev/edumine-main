# EduMine: Integrated Educational Data Mining Framework

**EduMine** is an integrated data mining and machine learning web platform designed to analyze student academic and behavioral records, discover hidden educational patterns, predict academic risk, and provide early intervention insights.

---

## 🌟 Abstract & Core Capabilities

> **EduMine** analyzes student academic and behavioral data, discovers meaningful patterns, and predicts academic risk. The project applies data cleaning, preprocessing, exploratory data analysis (EDA), feature selection, association rule mining, clustering, classification, regression, and anomaly detection. 
> 
> - **Association Rule Mining**: Discovers relationships among attendance, assignments, and examination performance.
> - **Clustering & Cohort Segmentation**: Identifies groups of students with similar academic characteristics and behaviors.
> - **Classification Models**: Predicts students who may be at academic risk for proactive counseling.
> - **Regression Models**: Estimates expected final marks or GPA.
> - **Feature Importance & Model Evaluation**: Assesses influential attributes (attendance, study hours, LMS engagement) and benchmarks algorithms.
> - **Early Intervention & What-If Simulation**: Provides personalized intervention recommendations and a live simulation sandbox.

---

## 🏗️ Architecture & Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Backend API** | Python 3.12, FastAPI, Uvicorn | High-performance asynchronous RESTful API |
| **Data Mining & ML** | Scikit-Learn, NumPy, Pandas | Supervised & Unsupervised Machine Learning |
| **Pattern Mining** | MLxtend & Native Vectorized Apriori | Frequent itemsets, Support, Confidence, Lift, Leverage |
| **Frontend UI** | Modern HTML5, Vanilla CSS3 (Glassmorphism), Chart.js | Interactive charts, canvas dependency graphs, dark/light luxury theme |
| **Data Formats** | CSV, XLSX, JSON | Custom institutional dataset uploader with auto-detection |

---

## 📂 Project Directory Structure

```text
edumine/
├── backend/
│   ├── __init__.py
│   ├── data_engine.py             # Data loader, column auto-detector, missing value & scaling
│   ├── eda_engine.py              # Descriptive statistics, correlations, feature distributions
│   ├── association_engine.py      # Apriori frequent itemsets & rule dependency miner
│   ├── clustering_engine.py       # K-Means, Hierarchical, DBSCAN, PCA 2D projection & personas
│   ├── classification_engine.py   # Multi-model risk prediction (Random Forest, GBM, SVM, etc.)
│   ├── regression_engine.py       # Continuous mark/GPA estimation (Gradient Boosting, Ridge, SVR)
│   ├── anomaly_engine.py          # Isolation Forest outlier detection with diagnostic root-causes
│   ├── intervention_engine.py     # Early warning intervention system & what-if simulator
│   ├── pipeline.py                # Coordinated end-to-end data mining pipeline
│   └── main.py                    # FastAPI application, REST endpoints & static file serving
├── frontend/
│   ├── index.html                 # Modern dashboard interface with 8 interactive modules
│   ├── css/
│   │   └── styles.css             # Design system: dark/light theme, glassmorphism, responsive grid
│   └── js/
│       └── app.js                 # Client state manager, Chart.js integrations & live simulator
├── data/
│   └── sample_students.csv        # 600 realistic student academic & engagement records
├── scripts/
│   └── generate_sample_data.py    # Synthetic dataset generator script
├── requirements.txt               # Python package dependencies
├── run.py                         # Single-command launcher (server + browser open)
└── README.md                      # Comprehensive documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run EduMine
Launch the server and launch the interactive web dashboard with a single command:
```bash
python run.py
```
Or directly via Uvicorn:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Web Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📊 Modules & Analytical Features

### 1. Overview & Dataset Explorer
- Real-time KPIs: Total Cohort Count, At-Risk Rate, Average Exam Score, Average Attendance.
- Searchable & paginated student data table with color-coded risk indicators.
- One-click dataset uploader for institutional CSV/Excel records.

### 2. Exploratory Data Analysis (EDA)
- Feature correlation heatmap (Pearson/Spearman coefficients).
- Histograms showing distributions of attendance, study hours, and exam scores.
- Risk cohort comparison charts and descriptive statistics table (mean, standard deviation, quartiles, skewness).

### 3. Association Rule Mining
- Discretizes continuous metrics into educational levels.
- Configurable minimum support, confidence, and lift thresholds.
- Interactive HTML5 Canvas visualization of the rule dependency network.
- Filters actionable high-risk indicators (e.g., `Low Attendance AND Low Study Hours => At-Risk`).

### 4. Student Clustering & Personas
- Unsupervised segmentation using **K-Means**, **Hierarchical Clustering**, or **DBSCAN**.
- 2D PCA projection scatter plot with interactive hover tooltips.
- Elbow Curve (SSE) and Silhouette Score analysis for optimal $k$.
- Automated cohort persona cards with tailored pedagogical actions:
  - *High-Flying Achievers* (Peer tutoring leaders)
  - *At-Risk / Disengaged Cohort* (Mandatory counseling & catch-up clinics)
  - *Consistent Moderate Performers* (Targeted booster sessions)

### 5. Academic Risk Classification
- Multi-model benchmarking: Random Forest, Gradient Boosting, Logistic Regression, SVM, Decision Tree, and KNN.
- Metric leaderboard: Accuracy, Precision, Recall, F1-Score, ROC-AUC, and 5-Fold Cross Validation.
- Mutual Information Feature Importance chart.
- Confusion Matrix and ROC Curve visualization.

### 6. Grade Regression
- Predicts expected final examination marks or cumulative GPA.
- Comparative evaluation across Gradient Boosting Regressor, Random Forest, Ridge, Lasso, and SVR.
- Actual vs. Predicted scatter plot with $y = x$ reference line.
- Residual error distribution histogram.

### 7. Anomaly Detection
- **Isolation Forest** outlier detection identifies atypical student trajectories.
- Automated root-cause diagnoses (e.g., *High attendance coupled with exam failure*, *Severe mid-semester performance cliff*).

### 8. Early Intervention & What-If Simulator
- Priority student intervention table sorted by academic urgency with specific action plans.
- **Interactive Real-Time What-If Simulator**: Adjust sliders for attendance, study hours, assignment completion, LMS hours, and midterm scores to observe live changes in predicted risk and expected grade.
