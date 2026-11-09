"""Interfaz web interactiva para la API de predicción de presión MiBici P2."""

from __future__ import annotations


def get_ui_html() -> str:
    """Retorna el documento HTML con la interfaz de usuario moderna para inferencia."""
    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MiBici — Predicción de Presión en Estaciones (P2)</title>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --primary-hover: #0284c7;
      --success: #22c55e;
      --success-bg: rgba(34, 197, 94, 0.15);
      --danger: #ef4444;
      --danger-bg: rgba(239, 68, 68, 0.15);
      --warning: #f59e0b;
      --warning-bg: rgba(245, 158, 11, 0.15);
      --radius: 12px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 24px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--card-border);
    }
    .brand h1 { font-size: 24px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 10px; }
    .brand p { color: var(--text-muted); font-size: 14px; margin-top: 4px; }
    .badges { display: flex; gap: 10px; flex-wrap: wrap; }
    .badge {
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      border: 1px solid var(--card-border);
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-muted);
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .badge-green { border-color: rgba(34, 197, 94, 0.4); color: var(--success); }
    .badge-blue { border-color: rgba(56, 189, 248, 0.4); color: var(--primary); }
    .badge:hover { filter: brightness(1.2); }

    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    @media (max-width: 860px) { .grid { grid-template-columns: 1fr; } }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius);
      padding: 24px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .card h2 { font-size: 18px; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }

    .presets-title { font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .presets { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
    .preset-btn {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--card-border);
      color: var(--text);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .preset-btn:hover { background: rgba(56, 189, 248, 0.15); border-color: var(--primary); }

    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .form-group { display: flex; flex-direction: column; gap: 6px; }
    .form-group.full { grid-column: span 2; }
    label { font-size: 13px; font-weight: 500; color: var(--text-muted); }
    input, select {
      background: #0f172a;
      border: 1px solid var(--card-border);
      color: #fff;
      padding: 10px 12px;
      border-radius: 6px;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s;
    }
    input:focus, select:focus { border-color: var(--primary); }

    .btn-submit {
      width: 100%;
      background: var(--primary);
      color: #0f172a;
      font-weight: 700;
      padding: 14px;
      border: none;
      border-radius: 8px;
      font-size: 15px;
      cursor: pointer;
      margin-top: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: background 0.2s, transform 0.1s;
    }
    .btn-submit:hover { background: var(--primary-hover); color: #fff; }
    .btn-submit:active { transform: scale(0.99); }

    .result-box {
      border: 2px dashed var(--card-border);
      border-radius: 8px;
      padding: 24px;
      min-height: 240px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      transition: all 0.3s;
    }
    .result-box.has-result { border-style: solid; }
    .result-icon { font-size: 48px; margin-bottom: 12px; }
    .result-title { font-size: 20px; font-weight: 700; margin-bottom: 8px; }
    .result-desc { font-size: 14px; color: var(--text-muted); max-width: 440px; line-height: 1.6; }
    .result-meta {
      display: flex;
      gap: 16px;
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      font-size: 13px;
      color: var(--text-muted);
    }
    .result-meta span b { color: #fff; }

    .state-normal { background: var(--success-bg); border-color: var(--success); color: #86efac; }
    .state-sin-bicis { background: var(--danger-bg); border-color: var(--danger); color: #fca5a5; }
    .state-sin-anclajes { background: var(--warning-bg); border-color: var(--warning); color: #fde047; }

    .json-toggle {
      margin-top: 20px;
      font-size: 13px;
      color: var(--primary);
      cursor: pointer;
      background: none;
      border: none;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    pre.json-viewer {
      background: #0f172a;
      border: 1px solid var(--card-border);
      border-radius: 6px;
      padding: 12px;
      font-size: 12px;
      color: #38bdf8;
      overflow-x: auto;
      margin-top: 10px;
      display: none;
      text-align: left;
    }
    .academic-notice {
      margin-top: 24px;
      padding: 14px 18px;
      background: rgba(255, 255, 255, 0.03);
      border-left: 3px solid var(--primary);
      border-radius: 4px;
      font-size: 13px;
      color: var(--text-muted);
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">
        <h1>🚲 MiBici — Inferencia de Presión en Estaciones</h1>
        <p>Modelo de clasificación supervisada P2 desplegado vía FastAPI y MLflow Model Registry</p>
      </div>
      <div class="badges">
        <span class="badge badge-green">● Servicio Online</span>
        <span class="badge">Modelo: Champion (v1)</span>
        <a class="badge badge-blue" href="/docs" target="_blank">📘 Swagger Docs</a>
        <a class="badge" href="/redoc" target="_blank">📄 ReDoc</a>
        <a class="badge" href="/health" target="_blank">🩺 Health</a>
      </div>
    </header>

    <div class="grid">
      <!-- Columna 1: Formulario interactivo -->
      <div class="card">
        <h2>⚙️ Parámetros de la Estación</h2>

        <div class="presets-title">Cargar Escenario Predefinido</div>
        <div class="presets">
          <button class="preset-btn" onclick="applyPreset('balanced')">🟢 Flujo Normal</button>
          <button class="preset-btn" onclick="applyPreset('no_bikes')">⚠️ Riesgo Sin Bicis</button>
          <button class="preset-btn" onclick="applyPreset('no_docks')">🛑 Riesgo Sin Anclajes</button>
        </div>

        <form id="predict-form" onsubmit="event.preventDefault(); runPrediction();">
          <div class="form-grid">
            <div class="form-group">
              <label for="capacity">Capacidad de anclajes</label>
              <input type="number" id="capacity" min="1" max="100" value="15" required>
            </div>
            <div class="form-group">
              <label for="day_of_week">Día de la semana</label>
              <select id="day_of_week" required>
                <option value="0">Lunes (0)</option>
                <option value="1">Martes (1)</option>
                <option value="2" selected>Miércoles (2)</option>
                <option value="3">Jueves (3)</option>
                <option value="4">Viernes (4)</option>
                <option value="5">Sábado (5)</option>
                <option value="6">Domingo (6)</option>
              </select>
            </div>
            <div class="form-group">
              <label for="hour">Hora de inicio (0-23)</label>
              <input type="number" id="hour" min="0" max="23" value="8" required>
            </div>
            <div class="form-group">
              <label for="minute">Minuto</label>
              <select id="minute" required>
                <option value="0" selected>:00</option>
                <option value="30">:30</option>
              </select>
            </div>
            <div class="form-group">
              <label for="departures_prev_30m">Salidas últimos 30 min</label>
              <input type="number" id="departures_prev_30m" min="0" value="2" required>
            </div>
            <div class="form-group">
              <label for="arrivals_prev_30m">Llegadas últimos 30 min</label>
              <input type="number" id="arrivals_prev_30m" min="0" value="2" required>
            </div>
            <div class="form-group">
              <label for="departures_prev_2h">Salidas últimas 2 horas</label>
              <input type="number" id="departures_prev_2h" min="0" value="8" required>
            </div>
            <div class="form-group">
              <label for="arrivals_prev_2h">Llegadas últimas 2 horas</label>
              <input type="number" id="arrivals_prev_2h" min="0" value="8" required>
            </div>
          </div>

          <button type="submit" class="btn-submit" id="btn-submit">
            <span>⚡ Estimar Presión en Estación</span>
          </button>
        </form>
      </div>

      <!-- Columna 2: Resultado de la Inferencia -->
      <div class="card">
        <h2>📊 Diagnóstico Operativo</h2>

        <div id="result-box" class="result-box">
          <div class="result-icon">🚲</div>
          <div class="result-title">Listo para predecir</div>
          <div class="result-desc">
            Ajusta los parámetros de la estación o selecciona un escenario predefinido y haz clic en <b>"Estimar Presión"</b> para consultar el modelo en tiempo real.
          </div>
        </div>

        <button class="json-toggle" onclick="toggleJson()">
          <span>▶ Ver petición y respuesta JSON (cURL)</span>
        </button>
        <pre id="json-viewer" class="json-viewer"></pre>
      </div>
    </div>

    <div class="academic-notice">
      <b>Aviso Académico MiBici:</b> El modelo estima un <b>proxy operacional de presión neta de movimientos</b> a partir de los viajes registrados y capacidad de anclajes. No mide la disponibilidad física de inventario en tiempo real.
    </div>
  </div>

  <script>
    const presets = {
      balanced: {
        capacity: 16, day_of_week: 2, hour: 12, minute: 0,
        departures_prev_30m: 2, arrivals_prev_30m: 2,
        departures_prev_2h: 8, arrivals_prev_2h: 8
      },
      no_bikes: {
        capacity: 15, day_of_week: 0, hour: 8, minute: 0,
        departures_prev_30m: 14, arrivals_prev_30m: 1,
        departures_prev_2h: 35, arrivals_prev_2h: 3
      },
      no_docks: {
        capacity: 14, day_of_week: 4, hour: 18, minute: 30,
        departures_prev_30m: 1, arrivals_prev_30m: 15,
        departures_prev_2h: 4, arrivals_prev_2h: 38
      }
    };

    function applyPreset(key) {
      const p = presets[key];
      if (!p) return;
      Object.keys(p).forEach(k => {
        const el = document.getElementById(k);
        if (el) el.value = p[k];
      });
      runPrediction();
    }

    async function runPrediction() {
      const btn = document.getElementById('btn-submit');
      const box = document.getElementById('result-box');
      const jsonViewer = document.getElementById('json-viewer');

      btn.disabled = true;
      btn.innerHTML = '<span>⏳ Consultando modelo...</span>';

      const payload = {
        capacity: parseInt(document.getElementById('capacity').value, 10),
        day_of_week: parseInt(document.getElementById('day_of_week').value, 10),
        hour: parseInt(document.getElementById('hour').value, 10),
        minute: parseInt(document.getElementById('minute').value, 10),
        departures_prev_30m: parseInt(document.getElementById('departures_prev_30m').value, 10),
        arrivals_prev_30m: parseInt(document.getElementById('arrivals_prev_30m').value, 10),
        departures_prev_2h: parseInt(document.getElementById('departures_prev_2h').value, 10),
        arrivals_prev_2h: parseInt(document.getElementById('arrivals_prev_2h').value, 10)
      };

      const t0 = performance.now();
      try {
        const response = await fetch('/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const latency = (performance.now() - t0).toFixed(1);
        const data = await response.json();

        box.className = 'result-box has-result';

        if (!response.ok) {
          box.innerHTML = `
            <div class="result-icon">❌</div>
            <div class="result-title" style="color: #ef4444">Error de Validación (422)</div>
            <div class="result-desc">${JSON.stringify(data.detail || data)}</div>
          `;
        } else {
          renderResult(box, data.prediction, data.model_name, data.model_version, latency);
        }

        jsonViewer.textContent = `# cURL de prueba:\\ncurl -X POST http://localhost:8000/predict \\\\\\n  -H "Content-Type: application/json" \\\\\\n  -d '${JSON.stringify(payload)}'\\n\\n# Respuesta (${latency} ms):\\n${JSON.stringify(data, null, 2)}`;
      } catch (err) {
        box.className = 'result-box has-result';
        box.innerHTML = `
          <div class="result-icon">⚠️</div>
          <div class="result-title" style="color: #ef4444">Fallo de Conexión</div>
          <div class="result-desc">${err.message}</div>
        `;
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>⚡ Estimar Presión en Estación</span>';
      }
    }

    function renderResult(box, prediction, modelName, modelVersion, latency) {
      if (prediction === 'sin_presion_neta_elevada') {
        box.className = 'result-box has-result state-normal';
        box.innerHTML = `
          <div class="result-icon">✅</div>
          <div class="result-title">Flujo Balanceado (Normal)</div>
          <div class="result-desc">
            La estación conserva equilibrio de flujo. No se proyecta escasez de bicicletas ni saturación de anclajes en los próximos 30 minutos.
          </div>
          <div class="result-meta">
            <span>Modelo: <b>${modelName}</b></span>
            <span>Versión: <b>${modelVersion}</b></span>
            <span>Latencia: <b>${latency} ms</b></span>
          </div>
        `;
      } else if (prediction === 'presion_sin_bicicletas') {
        box.className = 'result-box has-result state-sin-bicis';
        box.innerHTML = `
          <div class="result-icon">⚠️</div>
          <div class="result-title">Alerta: Presión Sin Bicicletas</div>
          <div class="result-desc">
            La tasa de salidas excede críticamente a las llegadas. Alto riesgo de estación vacía en el siguiente intervalo. Se sugiere programar reabastecimiento.
          </div>
          <div class="result-meta">
            <span>Modelo: <b>${modelName}</b></span>
            <span>Versión: <b>${modelVersion}</b></span>
            <span>Latencia: <b>${latency} ms</b></span>
          </div>
        `;
      } else if (prediction === 'presion_sin_anclajes') {
        box.className = 'result-box has-result state-sin-anclajes';
        box.innerHTML = `
          <div class="result-icon">🛑</div>
          <div class="result-title">Alerta: Presión Sin Anclajes</div>
          <div class="result-desc">
            La tasa de llegadas supera la absorción de la estación. Riesgo de que los usuarios no encuentren anclajes libres para devolver unidades.
          </div>
          <div class="result-meta">
            <span>Modelo: <b>${modelName}</b></span>
            <span>Versión: <b>${modelVersion}</b></span>
            <span>Latencia: <b>${latency} ms</b></span>
          </div>
        `;
      } else {
        box.className = 'result-box has-result';
        box.innerHTML = `
          <div class="result-icon">ℹ️</div>
          <div class="result-title">${prediction}</div>
          <div class="result-desc">Predicción generada por el modelo P2.</div>
        `;
      }
    }

    function toggleJson() {
      const el = document.getElementById('json-viewer');
      el.style.display = (el.style.display === 'block') ? 'none' : 'block';
    }
  </script>
</body>
</html>
"""
