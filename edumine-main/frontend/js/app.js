// EduMine Client Application Logic
document.addEventListener('DOMContentLoaded', () => {
  // Global State
  const state = {
    summary: null,
    preview: null,
    charts: {},
    currentTab: 'tabOverview',
    theme: localStorage.getItem('edumine_theme') || 'dark',
    selectedFile: null
  };

  // Set Theme
  document.documentElement.setAttribute('data-theme', state.theme);
  updateThemeIcon();

  // Initialize Event Listeners
  initNavigation();
  initThemeToggle();
  initUploadModal();
  initAssociationControls();
  initClusteringControls();
  initAnomalyControls();
  initSimulatorControls();
  initActionButtons();

  // Load Initial Data
  loadAllData();

  // -------------------------------------------------------------
  // Navigation & Tabs
  // -------------------------------------------------------------
  function initNavigation() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetTab = btn.getAttribute('data-tab');
        if (targetTab === state.currentTab) return;

        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        const pane = document.getElementById(targetTab);
        if (pane) pane.classList.add('active');

        state.currentTab = targetTab;

        // Trigger resize on charts in active pane to prevent rendering glitches
        setTimeout(() => {
          Object.values(state.charts).forEach(c => c && c.resize && c.resize());
          if (targetTab === 'tabAssociation') drawRuleNetwork();
        }, 150);
      });
    });
  }

  // -------------------------------------------------------------
  // Theme Toggle
  // -------------------------------------------------------------
  function initThemeToggle() {
    const btn = document.getElementById('btnThemeToggle');
    btn.addEventListener('click', () => {
      state.theme = state.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', state.theme);
      localStorage.setItem('edumine_theme', state.theme);
      updateThemeIcon();
      // Redraw charts with adapted colors
      loadEDA();
      loadClustering();
      loadClassification();
      loadRegression();
    });
  }

  function updateThemeIcon() {
    const btn = document.getElementById('btnThemeToggle');
    btn.innerHTML = state.theme === 'dark' ? '<i class="fa-solid fa-moon"></i>' : '<i class="fa-solid fa-sun" style="color: #f59e0b;"></i>';
  }

  // -------------------------------------------------------------
  // Core Data Fetchers
  // -------------------------------------------------------------
  async function loadAllData() {
    await loadSummary();
    await loadPreview();
    loadEDA();
    loadAssociationRules();
    loadClustering();
    loadClassification();
    loadRegression();
    loadAnomalies();
    loadInterventions();
  }

  // 1. Overview & Summary
  async function loadSummary() {
    try {
      const res = await fetch('/api/summary');
      const data = await res.json();
      state.summary = data;

      document.getElementById('pillStudentCount').textContent = `${data.total_students} Students`;
      document.getElementById('pillRiskRate').textContent = `At-Risk: ${data.risk_percentage}%`;
      
      document.getElementById('kpiTotalStudents').textContent = data.total_students;
      document.getElementById('kpiRiskRate').textContent = `${data.risk_percentage}%`;
      document.getElementById('kpiRiskCount').textContent = data.risk_students_count;
      document.getElementById('kpiAvgScore').textContent = data.average_score > 0 ? `${data.average_score}/100` : '--';
      document.getElementById('kpiAvgAttendance').textContent = `${data.average_attendance}%`;
      document.getElementById('badgeTotalRecords').textContent = `${data.total_students} Records`;
    } catch (err) {
      console.error('Error fetching summary:', err);
    }
  }

  // Preview Table
  async function loadPreview() {
    try {
      const res = await fetch('/api/preview?limit=100');
      const data = await res.json();
      state.preview = data;

      renderPreviewTable(data.records, data.columns);

      // Search functionality
      const searchInput = document.getElementById('tableSearchInput');
      searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
          renderPreviewTable(data.records, data.columns);
          return;
        }
        const filtered = data.records.filter(r => 
          Object.values(r).some(val => val !== null && String(val).toLowerCase().includes(query))
        );
        renderPreviewTable(filtered, data.columns);
      });
    } catch (err) {
      console.error('Error fetching preview data:', err);
    }
  }

  function renderPreviewTable(records, columns) {
    const headersTr = document.getElementById('studentTableHeaders');
    const tbody = document.getElementById('studentTableBody');

    if (!records || records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding: 2rem;">No matching student records found.</td></tr>';
      return;
    }

    // Display top 8 columns if wide
    const displayCols = columns && columns.length > 0 ? columns : Object.keys(records[0]);
    headersTr.innerHTML = displayCols.map(c => `<th>${c.replace(/_/g, ' ')}</th>`).join('');

    tbody.innerHTML = records.slice(0, 50).map(r => {
      return `<tr>
        ${displayCols.map(col => {
          const val = r[col];
          if (typeof val === 'string' && (val.toLowerCase() === 'at-risk' || val.toLowerCase() === 'high-risk')) {
            return `<td><span class="badge badge-danger">${val}</span></td>`;
          } else if (typeof val === 'string' && (val.toLowerCase() === 'safe' || val.toLowerCase() === 'low-risk')) {
            return `<td><span class="badge badge-success">${val}</span></td>`;
          }
          return `<td>${val !== null && val !== undefined ? val : '-'}</td>`;
        }).join('')}
      </tr>`;
    }).join('');
  }

  // 2. EDA Analysis
  async function loadEDA() {
    try {
      const res = await fetch('/api/eda');
      const data = await res.json();

      // Render Correlation Table
      if (data.correlation && data.correlation.columns) {
        const headers = document.getElementById('corrHeaders');
        const body = document.getElementById('corrBody');
        headers.innerHTML = `<th>Feature</th>` + data.correlation.columns.map(c => `<th style="max-width: 80px; font-size: 0.7rem;">${c.replace(/_/g, ' ')}</th>`).join('');

        body.innerHTML = data.correlation.columns.map((c, i) => {
          return `<tr>
            <td style="font-weight: 600; font-size: 0.75rem;">${c.replace(/_/g, ' ')}</td>
            ${data.correlation.values[i].map(val => {
              const absVal = Math.abs(val);
              const isPos = val > 0;
              const bg = isPos ? `rgba(99, 102, 241, ${absVal * 0.7})` : `rgba(239, 68, 68, ${absVal * 0.7})`;
              return `<td style="background-color: ${bg}; text-align: center; font-size: 0.75rem; font-weight: 600;">${val}</td>`;
            }).join('')}
          </tr>`;
        }).join('');
      }

      // Attendance Distribution Chart
      if (data.distributions && data.distributions['Attendance_Percentage']) {
        const dist = data.distributions['Attendance_Percentage'];
        renderBarChart('chartAttendanceDist', dist.labels, dist.counts, 'Attendance (%) Density', '#06b6d4');
      }

      // Study Hours Distribution Chart
      const studyKey = Object.keys(data.distributions || {}).find(k => k.toLowerCase().includes('study'));
      if (studyKey && data.distributions[studyKey]) {
        const dist = data.distributions[studyKey];
        renderBarChart('chartStudyDist', dist.labels, dist.counts, 'Study Hours/Week Density', '#8b5cf6');
      }

      // Risk Comparison Chart
      if (data.risk_comparisons) {
        const keys = Object.keys(data.risk_comparisons).slice(0, 5);
        const atRiskValues = keys.map(k => data.risk_comparisons[k]['At-Risk'] || data.risk_comparisons[k]['at-risk'] || 0);
        const safeValues = keys.map(k => data.risk_comparisons[k]['Safe'] || data.risk_comparisons[k]['safe'] || 0);

        renderGroupedBarChart('chartRiskComparison', keys.map(k => k.replace(/_/g, ' ')), [
          { label: 'At-Risk Students', data: atRiskValues, backgroundColor: '#ef4444' },
          { label: 'Safe Students', data: safeValues, backgroundColor: '#10b981' }
        ]);
      }

      // Descriptive Statistics Table
      if (data.statistics) {
        const tbody = document.getElementById('descStatsBody');
        tbody.innerHTML = Object.entries(data.statistics).map(([feat, s]) => {
          return `<tr>
            <td style="font-weight: 600;">${feat.replace(/_/g, ' ')}</td>
            <td>${s.mean}</td>
            <td>${s.std}</td>
            <td>${s.min}</td>
            <td>${s.q25}</td>
            <td style="font-weight: 600; color: var(--accent-secondary);">${s.median}</td>
            <td>${s.q75}</td>
            <td>${s.max}</td>
            <td>${s.skew}</td>
          </tr>`;
        }).join('');
      }
    } catch (err) {
      console.error('Error fetching EDA data:', err);
    }
  }

  // 3. Association Rules
  function initAssociationControls() {
    const sSupp = document.getElementById('sliderSupport');
    const sConf = document.getElementById('sliderConfidence');
    const sLift = document.getElementById('sliderLift');

    sSupp.addEventListener('input', e => document.getElementById('valSupport').textContent = e.target.value);
    sConf.addEventListener('input', e => document.getElementById('valConfidence').textContent = e.target.value);
    sLift.addEventListener('input', e => document.getElementById('valLift').textContent = e.target.value);

    document.getElementById('btnMineRules').addEventListener('click', () => {
      loadAssociationRules();
    });
  }

  async function loadAssociationRules() {
    const supp = document.getElementById('sliderSupport').value;
    const conf = document.getElementById('sliderConfidence').value;
    const lift = document.getElementById('sliderLift').value;

    try {
      const res = await fetch(`/api/association?min_support=${supp}&min_confidence=${conf}&min_lift=${lift}`);
      const data = await res.json();
      state.associationData = data;

      document.getElementById('badgeRuleCount').textContent = `${data.total_rules_found} Rules Discovered`;

      const tbody = document.getElementById('rulesTableBody');
      if (!data.rules || data.rules.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 2rem;">No rules found with current thresholds. Try reducing minimum support or confidence.</td></tr>';
      } else {
        tbody.innerHTML = data.rules.map((r, i) => {
          const isRisk = r.is_risk_related;
          const badgeClass = isRisk ? 'badge-danger' : (r.lift > 2.0 ? 'badge-warning' : 'badge-info');
          return `<tr>
            <td style="font-weight: 700; color: var(--accent-secondary);">#${i + 1}</td>
            <td>${r.antecedents.map(a => `<span class="badge badge-info" style="margin-right: 4px;">${a}</span>`).join('')}</td>
            <td style="color: var(--accent-primary); font-weight: 700;"><i class="fa-solid fa-arrow-right"></i></td>
            <td>${r.consequents.map(c => `<span class="badge ${isRisk ? 'badge-danger' : 'badge-success'}" style="margin-right: 4px;">${c}</span>`).join('')}</td>
            <td>${(r.support * 100).toFixed(1)}%</td>
            <td style="font-weight: 600;">${(r.confidence * 100).toFixed(1)}%</td>
            <td style="font-weight: 700; color: var(--accent-secondary);">${r.lift}x</td>
            <td><span class="badge ${badgeClass}">${isRisk ? 'Academic Risk Alert' : 'Strong Association'}</span></td>
          </tr>`;
        }).join('');
      }

      drawRuleNetwork();
    } catch (err) {
      console.error('Error fetching association rules:', err);
    }
  }

  function drawRuleNetwork() {
    const canvas = document.getElementById('networkCanvas');
    if (!canvas || !state.associationData || !state.associationData.network_graph) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.parentElement.clientWidth;
    const height = 380;
    canvas.width = width;
    canvas.height = height;

    const graph = state.associationData.network_graph;
    if (!graph.nodes || graph.nodes.length === 0) {
      ctx.fillStyle = '#94a3b8';
      ctx.font = '14px Inter';
      ctx.textAlign = 'center';
      ctx.fillText('No active rule network nodes to display', width / 2, height / 2);
      return;
    }

    ctx.clearRect(0, 0, width, height);

    // Layout nodes symmetrically on circles or force
    const nodeCoords = {};
    const n = graph.nodes.length;
    graph.nodes.forEach((node, i) => {
      const angle = (i / n) * 2 * Math.PI;
      const radius = node.type === 'rule' ? 90 : 145;
      nodeCoords[node.id] = {
        x: width / 2 + radius * Math.cos(angle) + (Math.sin(i) * 20),
        y: height / 2 + radius * Math.sin(angle) * 0.85
      };
    });

    // Draw Links
    ctx.lineWidth = 1.5;
    graph.links.forEach(link => {
      const p1 = nodeCoords[link.source];
      const p2 = nodeCoords[link.target];
      if (p1 && p2) {
        ctx.beginPath();
        ctx.strokeStyle = 'rgba(99, 102, 241, 0.35)';
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      }
    });

    // Draw Nodes
    graph.nodes.forEach(node => {
      const coord = nodeCoords[node.id];
      if (!coord) return;

      ctx.beginPath();
      const r = node.type === 'rule' ? 8 : (node.type === 'consequent' ? 14 : 10);
      ctx.arc(coord.x, coord.y, r, 0, 2 * Math.PI);

      if (node.type === 'rule') {
        ctx.fillStyle = '#ec4899';
      } else if (node.type === 'consequent') {
        ctx.fillStyle = node.name.toLowerCase().includes('risk') ? '#ef4444' : '#10b981';
      } else {
        ctx.fillStyle = '#6366f1';
      }
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Node label
      ctx.fillStyle = '#f8fafc';
      ctx.font = '10px Inter';
      ctx.textAlign = 'center';
      const shortName = node.name.length > 20 ? node.name.substring(0, 18) + '...' : node.name;
      ctx.fillText(shortName, coord.x, coord.y + r + 12);
    });
  }

  // 4. Clustering & Personas
  function initClusteringControls() {
    const sClusters = document.getElementById('sliderClusters');
    sClusters.addEventListener('input', e => document.getElementById('valClusters').textContent = e.target.value);
    document.getElementById('btnRunClustering').addEventListener('click', () => loadClustering());
  }

  async function loadClustering() {
    const k = document.getElementById('sliderClusters').value;
    const algo = document.getElementById('clusterAlgoSelect').value;

    try {
      const res = await fetch(`/api/clustering?n_clusters=${k}&algorithm=${algo}`);
      const data = await res.json();

      document.getElementById('badgeSilhouette').textContent = `Silhouette Score: ${data.silhouette_score}`;

      // Render Personas
      const pGrid = document.getElementById('clusterPersonasGrid');
      pGrid.innerHTML = (data.personas || []).map(p => {
        const topTraits = Object.entries(p.attributes || {}).slice(0, 4);
        return `<div class="persona-card" style="border-top: 4px solid ${p.color};">
          <div class="persona-title">
            <span>${p.title}</span>
            <span class="badge ${p.tone === 'danger' ? 'badge-danger' : (p.tone === 'success' ? 'badge-success' : 'badge-info')}">${p.percentage}%</span>
          </div>
          <div class="persona-meta">
            <span><i class="fa-solid fa-users"></i> ${p.size} Students</span>
            <span><i class="fa-solid fa-triangle-exclamation"></i> Risk: ${p.risk_percentage}%</span>
          </div>
          <ul class="persona-traits">
            ${topTraits.map(([k, v]) => `<li><span>${k.replace(/_/g, ' ')}</span><strong>${v}</strong></li>`).join('')}
          </ul>
          <div class="persona-action">
            <strong>Target Action:</strong> ${p.recommended_action}
          </div>
        </div>`;
      }).join('');

      // Render 2D PCA Scatter Chart
      renderPcaScatterChart('chartClusterPCA', data.points, data.personas);

      // Render Elbow Chart
      if (data.elbow_data) {
        renderElbowChart('chartElbow', data.elbow_data);
      }
    } catch (err) {
      console.error('Error fetching clustering data:', err);
    }
  }

  function renderPcaScatterChart(canvasId, points, personas) {
    if (!points) return;
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (state.charts[canvasId]) state.charts[canvasId].destroy();

    const clusterColors = {};
    (personas || []).forEach(p => {
      clusterColors[p.cluster_id] = p.color;
    });

    const datasets = [];
    const grouped = {};
    points.forEach(pt => {
      if (!grouped[pt.cluster]) grouped[pt.cluster] = [];
      grouped[pt.cluster].push({ x: pt.x, y: pt.y, raw: pt });
    });

    Object.entries(grouped).forEach(([cId, pts]) => {
      datasets.push({
        label: `Cluster ${cId}`,
        data: pts,
        backgroundColor: clusterColors[cId] || '#6366f1',
        pointRadius: 4.5,
        pointHoverRadius: 7
      });
    });

    state.charts[canvasId] = new Chart(ctx, {
      type: 'scatter',
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: getTextColor() } },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const pt = ctx.raw.raw;
                return `${pt.name} (${pt.id}) | Risk: ${pt.risk} | Score: ${pt.score || 'N/A'}`;
              }
            }
          }
        },
        scales: {
          x: { title: { display: true, text: 'Principal Component 1 (Academic Factor)', color: getTextColor() }, grid: { color: getGridColor() } },
          y: { title: { display: true, text: 'Principal Component 2 (Behavioral Factor)', color: getTextColor() }, grid: { color: getGridColor() } }
        }
      }
    });
  }

  function renderElbowChart(canvasId, elbowData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (state.charts[canvasId]) state.charts[canvasId].destroy();

    state.charts[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: elbowData.map(d => `k=${d.k}`),
        datasets: [
          {
            label: 'SSE / Inertia (Lower = Better)',
            data: elbowData.map(d => d.sse),
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            yAxisID: 'y'
          },
          {
            label: 'Silhouette Score (Higher = Better)',
            data: elbowData.map(d => d.silhouette),
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: getGridColor() } },
          y: { type: 'linear', display: true, position: 'left', grid: { color: getGridColor() } },
          y1: { type: 'linear', display: true, position: 'right', grid: { drawOnChartArea: false } }
        }
      }
    });
  }

  // 5. Risk Classification
  async function loadClassification() {
    try {
      const res = await fetch('/api/classification');
      const data = await res.json();

      document.getElementById('badgeBestClf').textContent = `Top Model: ${data.best_model}`;

      // Leaderboard
      const tbody = document.getElementById('clfLeaderboardBody');
      tbody.innerHTML = (data.models_evaluation || []).map((m, i) => {
        const isBest = m.model_name === data.best_model;
        return `<tr style="${isBest ? 'background: rgba(99, 102, 241, 0.08); font-weight: 600;' : ''}">
          <td>${i === 0 ? '<i class="fa-solid fa-crown" style="color: #f59e0b;"></i> #1' : `#${i + 1}`}</td>
          <td>${m.model_name} ${isBest ? '<span class="badge badge-success" style="margin-left: 6px;">Champion</span>' : ''}</td>
          <td style="color: var(--accent-secondary); font-weight: 700;">${m.accuracy}%</td>
          <td>${m.precision}%</td>
          <td>${m.recall}%</td>
          <td style="color: var(--color-success); font-weight: 700;">${m.f1_score}%</td>
          <td>${m.roc_auc}</td>
          <td>${m.cv_mean}% ± ${m.cv_std}%</td>
        </tr>`;
      }).join('');

      // Feature Importance
      if (data.feature_importance) {
        renderFeatureImportanceChart('chartFeatureImportance', data.feature_importance);
      }

      // Confusion Matrix
      if (data.confusion_matrix) {
        document.getElementById('cmTN').textContent = data.confusion_matrix.tn;
        document.getElementById('cmFP').textContent = data.confusion_matrix.fp;
        document.getElementById('cmFN').textContent = data.confusion_matrix.fn;
        document.getElementById('cmTP').textContent = data.confusion_matrix.tp;
      }

      // ROC Curve
      if (data.roc_curve) {
        renderRocCurve('chartROCCurve', data.roc_curve);
      }
    } catch (err) {
      console.error('Error fetching classification data:', err);
    }
  }

  function renderFeatureImportanceChart(canvasId, featureData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (state.charts[canvasId]) state.charts[canvasId].destroy();

    const labels = featureData.map(f => f.feature);
    const scores = featureData.map(f => f.importance);

    state.charts[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Mutual Information Importance',
          data: scores,
          backgroundColor: '#6366f1',
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: getGridColor() }, title: { display: true, text: 'Feature Importance Score', color: getTextColor() } },
          y: { grid: { display: false }, ticks: { color: getTextColor() } }
        }
      }
    });
  }

  function renderRocCurve(canvasId, rocData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (state.charts[canvasId]) state.charts[canvasId].destroy();

    const points = rocData.fpr.map((fpr, i) => ({ x: fpr, y: rocData.tpr[i] }));

    state.charts[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        datasets: [
          {
            label: `Classifier ROC (AUC = ${rocData.auc})`,
            data: points,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            fill: true,
            tension: 0.2
          },
          {
            label: 'Random Guess Baseline (AUC = 0.5)',
            data: [{ x: 0, y: 0 }, { x: 1, y: 1 }],
            borderColor: '#64748b',
            borderDash: [5, 5],
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { type: 'linear', min: 0, max: 1, title: { display: true, text: 'False Positive Rate' } },
          y: { type: 'linear', min: 0, max: 1, title: { display: true, text: 'True Positive Rate' } }
        }
      }
    });
  }

  // 6. Grade Regression
  async function loadRegression() {
    try {
      const res = await fetch('/api/regression');
      const data = await res.json();

      document.getElementById('badgeBestReg').textContent = `Top Regressor: ${data.best_model}`;

      // Leaderboard
      const tbody = document.getElementById('regLeaderboardBody');
      tbody.innerHTML = (data.models_evaluation || []).map((m, i) => {
        const isBest = m.model_name === data.best_model;
        return `<tr style="${isBest ? 'background: rgba(99, 102, 241, 0.08); font-weight: 600;' : ''}">
          <td>${i === 0 ? '<i class="fa-solid fa-crown" style="color: #f59e0b;"></i> #1' : `#${i + 1}`}</td>
          <td>${m.model_name} ${isBest ? '<span class="badge badge-success" style="margin-left: 6px;">Champion</span>' : ''}</td>
          <td style="color: var(--accent-secondary); font-weight: 700;">${m.r2_score}</td>
          <td>${m.r2_percentage}%</td>
          <td style="color: var(--color-danger);">${m.rmse}</td>
          <td>${m.mae}</td>
          <td>${m.cv_r2_mean} ± ${m.cv_r2_std}</td>
        </tr>`;
      }).join('');

      // Actual vs Predicted Chart
      if (data.actual_vs_predicted) {
        renderActualVsPredChart('chartActualVsPred', data.actual_vs_predicted);
      }

      // Residuals Chart
      if (data.residuals) {
        renderBarChart('chartResiduals', data.residuals.labels, data.residuals.counts, 'Residual Error Frequency', '#ec4899');
      }
    } catch (err) {
      console.error('Error fetching regression data:', err);
    }
  }

  function renderActualVsPredChart(canvasId, points) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (state.charts[canvasId]) state.charts[canvasId].destroy();

    const dataPoints = points.map(p => ({ x: p.actual, y: p.predicted }));

    state.charts[canvasId] = new Chart(ctx, {
      type: 'scatter',
      data: {
        datasets: [
          {
            label: 'Predicted vs Actual Marks',
            data: dataPoints,
            backgroundColor: '#06b6d4',
            pointRadius: 5
          },
          {
            type: 'line',
            label: 'Perfect Fit Line (y = x)',
            data: [{ x: 30, y: 30 }, { x: 100, y: 100 }],
            borderColor: '#f59e0b',
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { title: { display: true, text: 'Actual Examination Score', color: getTextColor() }, grid: { color: getGridColor() } },
          y: { title: { display: true, text: 'Predicted Examination Score', color: getTextColor() }, grid: { color: getGridColor() } }
        }
      }
    });
  }

  // 7. Anomaly Detection
  function initAnomalyControls() {
    const sContam = document.getElementById('sliderContamination');
    sContam.addEventListener('input', e => document.getElementById('valContamination').textContent = e.target.value);
    document.getElementById('btnScanAnomalies').addEventListener('click', () => loadAnomalies());
  }

  async function loadAnomalies() {
    const contam = document.getElementById('sliderContamination').value;
    try {
      const res = await fetch(`/api/anomalies?contamination=${contam}`);
      const data = await res.json();

      document.getElementById('badgeAnomalyCount').textContent = `Flagged: ${data.anomalies_detected} Outliers`;

      const tbody = document.getElementById('anomalyTableBody');
      if (!data.flagged_students || data.flagged_students.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 2rem;">No anomalous patterns detected with current sensitivity threshold.</td></tr>';
      } else {
        tbody.innerHTML = data.flagged_students.map(s => {
          return `<tr>
            <td style="font-weight: 700; color: var(--accent-secondary);">${s.id}</td>
            <td style="font-weight: 600;">${s.name}</td>
            <td><span class="badge ${s.risk_status.toLowerCase().includes('risk') ? 'badge-danger' : 'badge-success'}">${s.risk_status}</span></td>
            <td>${s.attendance !== null ? s.attendance + '%' : '-'}</td>
            <td>${s.study_hours !== null ? s.study_hours + 'h' : '-'}</td>
            <td style="font-weight: 700;">${s.exam_score !== null ? s.exam_score : '-'}</td>
            <td style="color: var(--color-danger); font-family: monospace;">${s.anomaly_score}</td>
            <td><span class="badge badge-warning" style="white-space: normal; text-align: left;">${s.primary_diagnosis}</span></td>
          </tr>`;
        }).join('');
      }
    } catch (err) {
      console.error('Error fetching anomalies:', err);
    }
  }

  // 8. Interventions & Simulator
  async function loadInterventions() {
    try {
      const res = await fetch('/api/interventions?limit=15');
      const data = await res.json();

      const tbody = document.getElementById('interventionTableBody');
      tbody.innerHTML = (data.interventions || []).map(item => {
        return `<tr>
          <td style="font-weight: 700; color: var(--accent-secondary);">${item.id}</td>
          <td style="font-weight: 600;">${item.name}</td>
          <td style="color: var(--color-danger); font-weight: 700;">${item.current_score !== null ? item.current_score + '/100' : 'N/A'}</td>
          <td>${item.attendance}%</td>
          <td><span class="badge ${item.urgency === 'CRITICAL' ? 'badge-danger' : 'badge-warning'}">${item.urgency}</span></td>
          <td>
            <ul style="padding-left: 1.2rem; font-size: 0.8rem; line-height: 1.4;">
              ${item.recommended_interventions.map(act => `<li>${act}</li>`).join('')}
            </ul>
          </td>
        </tr>`;
      }).join('');
    } catch (err) {
      console.error('Error fetching interventions:', err);
    }
  }

  function initSimulatorControls() {
    const inputs = ['simAttendance', 'simStudy', 'simAssign', 'simLMS', 'simMidterm', 'simFailures'];
    inputs.forEach(id => {
      const elem = document.getElementById(id);
      elem.addEventListener('input', () => {
        // Update label
        if (id === 'simAttendance') document.getElementById('simValAttendance').textContent = `${elem.value}%`;
        if (id === 'simStudy') document.getElementById('simValStudy').textContent = `${elem.value} hrs`;
        if (id === 'simAssign') document.getElementById('simValAssign').textContent = `${elem.value}%`;
        if (id === 'simLMS') document.getElementById('simValLMS').textContent = `${elem.value} hrs`;
        if (id === 'simMidterm') document.getElementById('simValMidterm').textContent = elem.value;
        if (id === 'simFailures') document.getElementById('simValFailures').textContent = elem.value;

        // Run live simulation inference
        runLiveSimulation();
      });
    });

    // Run first simulation
    runLiveSimulation();
  }

  let simDebounce = null;
  function runLiveSimulation() {
    clearTimeout(simDebounce);
    simDebounce = setTimeout(async () => {
      const payload = {
        data: {
          'Attendance_Percentage': parseFloat(document.getElementById('simAttendance').value),
          'Study_Hours_Per_Week': parseFloat(document.getElementById('simStudy').value),
          'Assignment_Completion_Rate': parseFloat(document.getElementById('simAssign').value),
          'LMS_Engagement_Hours': parseFloat(document.getElementById('simLMS').value),
          'Midterm_Score': parseFloat(document.getElementById('simMidterm').value),
          'Past_Failures': parseInt(document.getElementById('simFailures').value)
        }
      };

      try {
        const res = await fetch('/api/predict/single', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const result = await res.json();

        const risk = result.risk;
        const perf = result.performance;

        const probElem = document.getElementById('simRiskProbability');
        const statusElem = document.getElementById('simRiskStatus');
        const gaugeCircle = document.getElementById('simGaugeCircle');

        probElem.textContent = `${risk.risk_probability}%`;
        statusElem.textContent = risk.risk_status.toUpperCase();

        if (risk.is_at_risk) {
          gaugeCircle.style.borderColor = '#ef4444';
          gaugeCircle.style.background = 'radial-gradient(circle, rgba(239,68,68,0.2) 0%, rgba(239,68,68,0.04) 70%)';
          probElem.style.color = '#ef4444';
        } else {
          gaugeCircle.style.borderColor = '#10b981';
          gaugeCircle.style.background = 'radial-gradient(circle, rgba(16,185,129,0.2) 0%, rgba(16,185,129,0.04) 70%)';
          probElem.style.color = '#10b981';
        }

        document.getElementById('simPredictedScore').textContent = `${perf.predicted_value} / 100`;
        document.getElementById('simGradeLetter').textContent = `Grade Estimate: ${perf.grade_letter}`;

        // Recommendation
        const recElem = document.getElementById('simActionRecommendation');
        if (risk.is_at_risk) {
          recElem.innerHTML = `<strong>Suggested Action:</strong> Student is in danger of course failure. Mandate weekly advisor check-ins, homework clinic enrollments, and target +6 study hrs/week to reduce risk below 30%.`;
        } else {
          recElem.innerHTML = `<strong>Suggested Action:</strong> Student profile is on track. Encourage engagement in peer tutoring or advanced honors assignments.`;
        }
      } catch (err) {
        console.error('Error running live simulation:', err);
      }
    }, 200);
  }

  // -------------------------------------------------------------
  // Dataset Upload Modal & Reset
  // -------------------------------------------------------------
  function initUploadModal() {
    const modal = document.getElementById('uploadModal');
    const openBtn = document.getElementById('btnUploadModal');
    const closeBtn = document.getElementById('btnCloseModal');
    const cancelBtn = document.getElementById('btnCancelModal');
    const dropzone = document.getElementById('fileDropzone');
    const fileInput = document.getElementById('fileInput');
    const confirmBtn = document.getElementById('btnConfirmUpload');
    const statusMsg = document.getElementById('uploadStatusMsg');

    openBtn.addEventListener('click', () => modal.classList.add('active'));
    closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    cancelBtn.addEventListener('click', () => modal.classList.remove('active'));

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFileSelection(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFileSelection(e.target.files[0]);
      }
    });

    function handleFileSelection(file) {
      state.selectedFile = file;
      confirmBtn.removeAttribute('disabled');
      statusMsg.style.display = 'block';
      statusMsg.innerHTML = `<span style="color: var(--accent-secondary);"><i class="fa-solid fa-file"></i> Selected: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)</span>`;
    }

    confirmBtn.addEventListener('click', async () => {
      if (!state.selectedFile) return;

      confirmBtn.disabled = true;
      confirmBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';

      const formData = new FormData();
      formData.append('file', state.selectedFile);

      try {
        const res = await fetch('/api/dataset/upload', {
          method: 'POST',
          body: formData
        });
        const result = await res.json();

        if (res.ok) {
          document.getElementById('pillDatasetSource').textContent = state.selectedFile.name;
          modal.classList.remove('active');
          confirmBtn.innerHTML = '<i class="fa-solid fa-upload"></i> Upload & Process';
          loadAllData();
          alert(`Successfully uploaded and analyzed ${result.filename}!`);
        } else {
          throw new Error(result.detail || 'Upload failed');
        }
      } catch (err) {
        statusMsg.innerHTML = `<span style="color: var(--color-danger);"><i class="fa-solid fa-circle-exclamation"></i> Error: ${err.message}</span>`;
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = '<i class="fa-solid fa-upload"></i> Upload & Process';
      }
    });
  }

  function initActionButtons() {
    // Reset dataset
    document.getElementById('btnResetData').addEventListener('click', async () => {
      if (confirm('Reset to the standard sample student dataset?')) {
        await fetch('/api/dataset/reset', { method: 'POST' });
        document.getElementById('pillDatasetSource').textContent = 'sample_students.csv';
        loadAllData();
      }
    });

    // Run Full Pipeline
    const runBtn = document.getElementById('btnRunPipeline');
    runBtn.addEventListener('click', async () => {
      runBtn.disabled = true;
      runBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Pipeline...';
      try {
        await fetch('/api/pipeline/run-all');
        await loadAllData();
        runBtn.innerHTML = '<i class="fa-solid fa-check"></i> Pipeline Complete';
        setTimeout(() => {
          runBtn.disabled = false;
          runBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Run Pipeline';
        }, 1500);
      } catch (err) {
        console.error(err);
        runBtn.disabled = false;
        runBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Run Pipeline';
      }
    });
  }

  // -------------------------------------------------------------
  // Chart Helper Functions
  // -------------------------------------------------------------
  function getTextColor() {
    return state.theme === 'dark' ? '#94a3b8' : '#475569';
  }

  function getGridColor() {
    return state.theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
  }

  function renderBarChart(canvasId, labels, data, label, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (state.charts[canvasId]) state.charts[canvasId].destroy();

    state.charts[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: label,
          data: data,
          backgroundColor: color,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: getTextColor() } },
          y: { grid: { color: getGridColor() }, ticks: { color: getTextColor() } }
        }
      }
    });
  }

  function renderGroupedBarChart(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (state.charts[canvasId]) state.charts[canvasId].destroy();

    state.charts[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: datasets.map(d => ({ ...d, borderRadius: 6 }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: getTextColor() } }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: getTextColor() } },
          y: { grid: { color: getGridColor() }, ticks: { color: getTextColor() } }
        }
      }
    });
  }
});
