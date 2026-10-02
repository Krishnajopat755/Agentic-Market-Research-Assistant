"""HTML Dashboard for Agentic Market Research Assistant."""


def get_dashboard_html() -> str:
    """Return an ultra-premium, dark-mode interactive research dashboard."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agentic Market Research Assistant</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #07090e;
      --card-bg: rgba(16, 22, 36, 0.72);
      --card-border: rgba(255, 255, 255, 0.08);
      --card-hover: rgba(26, 35, 56, 0.85);
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --accent: #6366f1;
      --accent-glow: rgba(99, 102, 241, 0.25);
      --emerald: #10b981;
      --emerald-glow: rgba(16, 185, 129, 0.2);
      --rose: #f43f5e;
      --rose-glow: rgba(244, 63, 94, 0.2);
      --amber: #f59e0b;
      --amber-glow: rgba(245, 158, 11, 0.2);
      --cyan: #06b6d4;
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg);
      background-image:
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.1) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(14, 165, 233, 0.08) 0px, transparent 50%);
      color: var(--text);
      font-family: var(--font-sans);
      min-height: 100vh;
      line-height: 1.5;
      padding-bottom: 60px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #07090e; }
    ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #334155; }

    /* Header Nav */
    header {
      background: rgba(7, 9, 14, 0.85);
      backdrop-filter: blur(20px);
      border-bottom: 1px solid var(--card-border);
      position: sticky;
      top: 0;
      z-index: 50;
      padding: 14px 28px;
    }

    .nav-container {
      max-width: 1360px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: var(--text);
    }

    .brand-icon {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: linear-gradient(135deg, #6366f1, #06b6d4);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.2rem;
      color: #fff;
      box-shadow: 0 0 20px var(--accent-glow);
    }

    .brand-title {
      font-weight: 700;
      font-size: 1.15rem;
      letter-spacing: -0.02em;
    }

    .brand-sub {
      font-size: 0.75rem;
      color: var(--text-muted);
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
      font-size: 0.75rem;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 9999px;
      font-family: var(--font-mono);
    }

    .pulse-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 10px #10b981;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0% { transform: scale(0.95); opacity: 0.8; }
      50% { transform: scale(1.3); opacity: 1; }
      100% { transform: scale(0.95); opacity: 0.8; }
    }

    .nav-link {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 500;
      transition: color 0.15s ease;
      padding: 6px 12px;
      border-radius: 6px;
    }

    .nav-link:hover {
      color: var(--text);
      background: rgba(255, 255, 255, 0.05);
    }

    /* Main Container */
    main {
      max-width: 1360px;
      margin: 0 auto;
      padding: 28px 24px;
    }

    /* Control Panel */
    .control-panel {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    .control-row {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    .ticker-group {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .ticker-label {
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .ticker-pills {
      display: flex;
      gap: 6px;
    }

    .ticker-pill {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--card-border);
      color: var(--text);
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 0.85rem;
      font-family: var(--font-mono);
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .ticker-pill:hover {
      background: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.2);
    }

    .ticker-pill.active {
      background: linear-gradient(135deg, #4f46e5, #6366f1);
      border-color: #818cf8;
      color: #fff;
      box-shadow: 0 0 16px var(--accent-glow);
    }

    .custom-input {
      background: rgba(0, 0, 0, 0.45);
      border: 1px solid var(--card-border);
      color: var(--text);
      padding: 7px 12px;
      border-radius: 8px;
      font-family: var(--font-mono);
      font-size: 0.85rem;
      min-width: 250px;
      text-transform: uppercase;
      outline: none;
      transition: all 0.2s ease;
    }

    .custom-input:focus {
      border-color: #6366f1;
      box-shadow: 0 0 0 2px var(--accent-glow);
    }

    .btn-search {
      background: rgba(99, 102, 241, 0.25);
      border: 1px solid rgba(99, 102, 241, 0.5);
      color: #a5b4fc;
      padding: 7px 14px;
      border-radius: 8px;
      font-family: var(--font-sans);
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-search:hover {
      background: #6366f1;
      color: #fff;
      box-shadow: 0 0 12px var(--accent-glow);
    }

    .params-group {
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }

    .param-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .param-label {
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--text-dim);
      text-transform: uppercase;
    }

    .param-value {
      font-size: 0.85rem;
      font-family: var(--font-mono);
      color: var(--text);
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid var(--card-border);
      padding: 4px 10px;
      border-radius: 6px;
    }

    .action-group {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .btn-primary {
      background: linear-gradient(135deg, #4f46e5, #06b6d4);
      color: #fff;
      border: none;
      padding: 10px 22px;
      border-radius: 10px;
      font-size: 0.9rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
      box-shadow: 0 4px 16px var(--accent-glow);
    }

    .btn-primary:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 24px rgba(99, 102, 241, 0.4);
    }

    .btn-primary:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    .btn-secondary {
      background: rgba(255, 255, 255, 0.05);
      color: var(--text);
      border: 1px solid var(--card-border);
      padding: 9px 16px;
      border-radius: 10px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.1);
    }

    /* Stepper Workflow */
    .workflow-stepper {
      display: flex;
      justify-content: space-between;
      margin-top: 18px;
      padding-top: 16px;
      border-top: 1px solid var(--card-border);
      position: relative;
    }

    .step-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-dim);
      transition: color 0.3s;
    }

    .step-num {
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--card-border);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-mono);
      font-size: 0.7rem;
    }

    .step-item.active {
      color: #818cf8;
    }

    .step-item.active .step-num {
      background: #4f46e5;
      color: #fff;
      border-color: #818cf8;
      box-shadow: 0 0 10px var(--accent-glow);
    }

    .step-item.completed {
      color: #34d399;
    }

    .step-item.completed .step-num {
      background: #10b981;
      color: #07090e;
      border-color: #34d399;
    }

    /* Hero Report Card */
    .hero-card {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 28px;
      margin-bottom: 24px;
      position: relative;
      overflow: hidden;
    }

    .hero-glow-bullish {
      position: absolute;
      top: -100px;
      right: -100px;
      width: 320px;
      height: 320px;
      background: radial-gradient(circle, rgba(16, 185, 129, 0.18) 0%, transparent 70%);
      pointer-events: none;
    }

    .hero-glow-bearish {
      position: absolute;
      top: -100px;
      right: -100px;
      width: 320px;
      height: 320px;
      background: radial-gradient(circle, rgba(244, 63, 94, 0.18) 0%, transparent 70%);
      pointer-events: none;
    }

    .hero-glow-neutral {
      position: absolute;
      top: -100px;
      right: -100px;
      width: 320px;
      height: 320px;
      background: radial-gradient(circle, rgba(245, 158, 11, 0.18) 0%, transparent 70%);
      pointer-events: none;
    }

    .hero-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 20px;
    }

    .hero-symbol-group {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .hero-symbol {
      font-size: 2.2rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      font-family: var(--font-mono);
      background: linear-gradient(135deg, #fff 40%, var(--text-muted));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .state-pill {
      font-size: 0.85rem;
      font-weight: 800;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      padding: 6px 16px;
      border-radius: 9999px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .state-bullish {
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.4);
      box-shadow: 0 0 20px var(--emerald-glow);
    }

    .state-bearish {
      background: rgba(244, 63, 94, 0.15);
      color: #fb7185;
      border: 1px solid rgba(244, 63, 94, 0.4);
      box-shadow: 0 0 20px var(--rose-glow);
    }

    .state-neutral {
      background: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.4);
      box-shadow: 0 0 20px var(--amber-glow);
    }

    .hero-meta {
      display: flex;
      gap: 20px;
      font-size: 0.8rem;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }

    .hero-headline {
      font-size: 1.35rem;
      font-weight: 700;
      color: var(--text);
      line-height: 1.4;
      margin-bottom: 16px;
    }

    .hero-executive-box {
      background: rgba(0, 0, 0, 0.3);
      border-left: 4px solid var(--accent);
      border-radius: 0 10px 10px 0;
      padding: 18px 22px;
      color: #cbd5e1;
      font-size: 0.96rem;
      line-height: 1.7;
    }

    /* Score and Gauges Grid */
    .score-summary-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin-top: 24px;
    }

    .score-card {
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .score-title {
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-dim);
      text-transform: uppercase;
      margin-bottom: 8px;
    }

    .score-val {
      font-size: 1.8rem;
      font-weight: 800;
      font-family: var(--font-mono);
    }

    .score-bar-bg {
      height: 6px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 3px;
      margin-top: 10px;
      overflow: hidden;
      position: relative;
    }

    .score-bar-fill {
      height: 100%;
      border-radius: 3px;
      transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Metrics Grid */
    .grid-3 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
      gap: 20px;
      margin-bottom: 24px;
    }

    .panel-card {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 22px;
      display: flex;
      flex-direction: column;
    }

    .panel-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--card-border);
    }

    .panel-title {
      font-size: 1rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .panel-pill {
      font-size: 0.7rem;
      font-family: var(--font-mono);
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--card-border);
      padding: 2px 8px;
      border-radius: 6px;
      color: var(--text-muted);
    }

    /* Metric Key-Value List */
    .metric-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .metric-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.88rem;
    }

    .metric-name {
      color: var(--text-muted);
    }

    .metric-num {
      font-family: var(--font-mono);
      font-weight: 600;
      color: var(--text);
    }

    .metric-sub {
      font-size: 0.75rem;
      color: var(--text-dim);
      font-family: var(--font-sans);
      margin-left: 6px;
    }

    /* Contributors Table */
    .factors-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 0.84rem;
    }

    .factors-table th {
      text-align: left;
      color: var(--text-dim);
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--card-border);
    }

    .factors-table td {
      padding: 10px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      font-family: var(--font-mono);
    }

    .factor-bar-container {
      width: 100px;
      height: 6px;
      background: rgba(255, 255, 255, 0.06);
      border-radius: 3px;
      overflow: hidden;
      display: inline-block;
      vertical-align: middle;
      margin-right: 8px;
    }

    /* Headlines List */
    .news-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .news-item {
      background: rgba(0, 0, 0, 0.2);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 12px 14px;
      transition: background 0.15s;
    }

    .news-item:hover {
      background: rgba(255, 255, 255, 0.03);
    }

    .news-title {
      font-size: 0.88rem;
      font-weight: 600;
      color: var(--text);
      text-decoration: none;
      display: block;
      margin-bottom: 6px;
      line-height: 1.4;
    }

    .news-title:hover {
      color: #818cf8;
    }

    .news-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.72rem;
      color: var(--text-dim);
      font-family: var(--font-mono);
    }

    .news-sent-tag {
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
    }

    /* Tab switcher for Views */
    .view-tabs {
      display: flex;
      gap: 8px;
      border-bottom: 1px solid var(--card-border);
      margin-bottom: 20px;
      padding-bottom: 10px;
    }

    .tab-btn {
      background: none;
      border: none;
      color: var(--text-muted);
      font-family: var(--font-sans);
      font-size: 0.88rem;
      font-weight: 600;
      padding: 6px 14px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.15s;
    }

    .tab-btn.active {
      color: #fff;
      background: rgba(255, 255, 255, 0.08);
    }

    .tab-btn:hover:not(.active) {
      color: var(--text);
    }

    /* Evidence & Audit */
    .evidence-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.82rem;
      margin-top: 12px;
    }

    .evidence-table th {
      text-align: left;
      padding: 8px 12px;
      color: var(--text-dim);
      font-size: 0.72rem;
      text-transform: uppercase;
      border-bottom: 1px solid var(--card-border);
    }

    .evidence-table td {
      padding: 10px 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: var(--text-muted);
    }

    .claim-tag {
      font-family: var(--font-mono);
      color: #818cf8;
      font-weight: 600;
    }

    /* Code Block / JSON Preview */
    pre.code-view {
      background: #04060a;
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 18px;
      font-family: var(--font-mono);
      font-size: 0.8rem;
      color: #93c5fd;
      overflow-x: auto;
      max-height: 480px;
    }

    /* Regulatory Footer */
    .regulatory-footer {
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 16px 20px;
      margin-top: 36px;
      font-size: 0.76rem;
      color: var(--text-dim);
      line-height: 1.6;
    }

    /* Spinner */
    .spinner {
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      border-top-color: #fff;
      animation: spin 0.8s linear infinite;
      display: none;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <!-- Top Navigation -->
  <header>
    <div class="nav-container">
      <a href="/" class="brand">
        <div class="brand-icon">AG</div>
        <div>
          <div class="brand-title">Agentic Market Research Assistant</div>
          <div class="brand-sub">Deterministic Finance Core &bull; MCP Architecture</div>
        </div>
      </a>
      <div class="nav-actions">
        <div class="status-badge">
          <span class="pulse-dot"></span>
          <span>MCP ENGINE ONLINE</span>
        </div>
        <a href="/docs" target="_blank" class="nav-link">Swagger Docs</a>
        <a href="/redoc" target="_blank" class="nav-link">ReDoc</a>
        <a href="/health" target="_blank" class="nav-link">Health API</a>
      </div>
    </div>
  </header>

  <!-- Main App Body -->
  <main>
    <!-- Control Bar -->
    <div class="control-panel">
      <div class="control-row">
        <!-- Ticker Selection -->
        <div class="ticker-group">
          <span class="ticker-label">Watchlist:</span>
          <div class="ticker-pills">
            <button class="ticker-pill active" onclick="selectTicker('RELIANCE')">RELIANCE</button>
            <button class="ticker-pill" onclick="selectTicker('TCS')">TCS</button>
            <button class="ticker-pill" onclick="selectTicker('HDFCBANK')">HDFCBANK</button>
            <button class="ticker-pill" onclick="selectTicker('INFY')">INFY</button>
            <button class="ticker-pill" onclick="selectTicker('ICICIBANK')">ICICIBANK</button>
            <button class="ticker-pill" onclick="selectTicker('NIFTY')">NIFTY 50</button>
            <button class="ticker-pill" onclick="selectTicker('SENSEX')">SENSEX</button>
          </div>
          <div style="display: flex; gap: 6px; align-items: center;">
            <input type="text" id="customTicker" class="custom-input" list="niftyStocksList" placeholder="Search NIFTY 50 / SENSEX / Any NSE ticker..." maxlength="25" onkeyup="handleCustomTicker(event)" onchange="handleCustomTickerChange(event)">
            <button class="btn-search" onclick="submitCustomTicker()">Analyze</button>
          </div>
          <datalist id="niftyStocksList">
            <option value="RELIANCE">Reliance Industries Limited (Energy & Retail)</option>
            <option value="TCS">Tata Consultancy Services Limited (IT)</option>
            <option value="HDFCBANK">HDFC Bank Limited (Banking)</option>
            <option value="ICICIBANK">ICICI Bank Limited (Banking)</option>
            <option value="BHARTIARTL">Bharti Airtel Limited (Telecom)</option>
            <option value="INFY">Infosys Limited (IT)</option>
            <option value="ITC">ITC Limited (FMCG & Conglomerate)</option>
            <option value="SBIN">State Bank of India (PSU Banking)</option>
            <option value="LT">Larsen & Toubro Limited (Infrastructure)</option>
            <option value="HINDUNILVR">Hindustan Unilever Limited (FMCG)</option>
            <option value="AXISBANK">Axis Bank Limited (Banking)</option>
            <option value="KOTAKBANK">Kotak Mahindra Bank Limited (Banking)</option>
            <option value="BAJFINANCE">Bajaj Finance Limited (NBFC)</option>
            <option value="MARUTI">Maruti Suzuki India Limited (Automobile)</option>
            <option value="M&M">Mahindra & Mahindra Limited (Automobile)</option>
            <option value="TITAN">Titan Company Limited (Consumer)</option>
            <option value="SUNPHARMA">Sun Pharmaceutical Industries (Pharma)</option>
            <option value="ADANIENT">Adani Enterprises Limited (Commodities)</option>
            <option value="TATAMOTORS">Tata Motors Limited (Automobile)</option>
            <option value="ULTRACEMCO">UltraTech Cement Limited (Cement)</option>
            <option value="NTPC">NTPC Limited (Power)</option>
            <option value="ONGC">Oil and Natural Gas Corporation (Energy)</option>
            <option value="POWERGRID">Power Grid Corporation (Power)</option>
            <option value="TATASTEEL">Tata Steel Limited (Metals)</option>
            <option value="BAJAJFINSV">Bajaj Finserv Limited (Financials)</option>
            <option value="COALINDIA">Coal India Limited (Mining)</option>
            <option value="HCLTECH">HCL Technologies Limited (IT)</option>
            <option value="NESTLEIND">Nestle India Limited (FMCG)</option>
            <option value="ASIANPAINT">Asian Paints Limited (Paints)</option>
            <option value="JSWSTEEL">JSW Steel Limited (Metals)</option>
            <option value="GRASIM">Grasim Industries Limited (Conglomerate)</option>
            <option value="TECHM">Tech Mahindra Limited (IT)</option>
            <option value="HINDALCO">Hindalco Industries Limited (Metals)</option>
            <option value="CIPLA">Cipla Limited (Pharma)</option>
            <option value="ADANIPORTS">Adani Ports & SEZ (Ports)</option>
            <option value="TRENT">Trent Limited (Retail)</option>
            <option value="BEL">Bharat Electronics Limited (Defence)</option>
            <option value="SHRIRAMFIN">Shriram Finance Limited (NBFC)</option>
            <option value="DRREDDY">Dr. Reddy's Laboratories (Pharma)</option>
            <option value="BPCL">Bharat Petroleum Corporation (Oil)</option>
            <option value="EICHERMOT">Eicher Motors Limited (Auto)</option>
            <option value="WIPRO">Wipro Limited (IT)</option>
            <option value="APOLLOHOSP">Apollo Hospitals Enterprise (Healthcare)</option>
            <option value="HEROMOTOCO">Hero MotoCorp Limited (Auto)</option>
            <option value="TATACONSUM">Tata Consumer Products (FMCG)</option>
            <option value="BRITANNIA">Britannia Industries Limited (FMCG)</option>
            <option value="SBILIFE">SBI Life Insurance (Insurance)</option>
            <option value="HDFCLIFE">HDFC Life Insurance (Insurance)</option>
            <option value="INDUSINDBK">IndusInd Bank Limited (Banking)</option>
            <option value="DIVISLAB">Divi's Laboratories Limited (Pharma)</option>
            <option value="TATAPOWER">Tata Power Company Limited (Power)</option>
            <option value="JIOFIN">Jio Financial Services (Fintech)</option>
            <option value="ZOMATO">Zomato Limited (Delivery/Internet)</option>
            <option value="VEDL">Vedanta Limited (Resources)</option>
            <option value="HAL">Hindustan Aeronautics Limited (Defence)</option>
            <option value="NIFTY">NIFTY 50 Benchmark Index (^NSEI)</option>
            <option value="SENSEX">S&P BSE SENSEX 30 Index (^BSESN)</option>
          </datalist>
        </div>

        <!-- Parameters -->
        <div class="params-group">
          <div class="param-item">
            <span class="param-label">Execution Mode</span>
            <span class="param-value" style="color:#34d399;">LIVE (Real-Time Indian Equities)</span>
          </div>
          <div class="param-item">
            <span class="param-label">Market Universe</span>
            <span class="param-value" style="color:#38bdf8;">NIFTY 50 &bull; SENSEX</span>
          </div>
          <div class="param-item">
            <span class="param-label">Lookback Window</span>
            <span class="param-value">120 Days</span>
          </div>
          <div class="param-item">
            <span class="param-label">Signal Horizon</span>
            <span class="param-value">5 Daily Bars</span>
          </div>
        </div>

        <!-- Action Button -->
        <div class="action-group">
          <button id="runBtn" class="btn-primary" onclick="runAnalysis()">
            <span id="btnSpinner" class="spinner"></span>
            <span id="btnText">Run Research</span>
          </button>
        </div>
      </div>

      <!-- Workflow Stepper -->
      <div class="workflow-stepper">
        <div id="step-init" class="step-item completed">
          <div class="step-num">1</div>
          <span>INITIALIZED</span>
        </div>
        <div id="step-data" class="step-item completed">
          <div class="step-num">2</div>
          <span>DATA COLLECTION</span>
        </div>
        <div id="step-analytics" class="step-item completed">
          <div class="step-num">3</div>
          <span>ANALYTICS CORE</span>
        </div>
        <div id="step-synthesis" class="step-item completed">
          <div class="step-num">4</div>
          <span>AGENT SYNTHESIS</span>
        </div>
        <div id="step-complete" class="step-item completed">
          <div class="step-num">5</div>
          <span>REPORT READY</span>
        </div>
      </div>
    </div>

    <!-- Active Report Presentation Container -->
    <div id="reportContainer">
      <!-- Injected dynamically via JavaScript -->
    </div>

    <!-- Regulatory Notice Footer -->
    <div class="regulatory-footer">
      <strong>RESEARCH & COMPLIANCE NOTICE:</strong> This report is an automated research demonstration generated by the Agentic Market Research Assistant pair programming project. It does not constitute financial advice, investment recommendation, or an offer to buy or sell securities. Point-in-time constraints and lookahead bias prevention tests are strictly enforced at runtime.
    </div>
  </main>

  <script>
    let activeSymbol = "RELIANCE";
    let currentReport = null;
    let currentRunId = null;

    function selectTicker(sym) {
      activeSymbol = sym.toUpperCase();
      document.querySelectorAll(".ticker-pill").forEach(el => {
        const t = el.innerText.replace(" 50", "").trim();
        el.classList.toggle("active", t === activeSymbol || el.innerText === activeSymbol);
      });
      document.getElementById("customTicker").value = "";
      runAnalysis();
    }

    function submitCustomTicker() {
      const val = document.getElementById("customTicker").value.trim().toUpperCase();
      if (val) {
        activeSymbol = val;
        document.querySelectorAll(".ticker-pill").forEach(el => el.classList.remove("active"));
        runAnalysis();
      }
    }

    function handleCustomTickerChange(e) {
      const val = document.getElementById("customTicker").value.trim();
      if (val) {
        submitCustomTicker();
      }
    }

    function handleCustomTicker(e) {
      if (e.key === "Enter") {
        submitCustomTicker();
      }
    }

    async function runAnalysis() {
      const btn = document.getElementById("runBtn");
      const btnText = document.getElementById("btnText");
      const spinner = document.getElementById("btnSpinner");

      btn.disabled = true;
      spinner.style.display = "inline-block";
      btnText.innerText = "Analyzing " + activeSymbol + "...";

      // Animate stepper
      setStepperStage("init");
      await new Promise(r => setTimeout(r, 60));
      setStepperStage("data");

      try {
        const payload = {
          symbols: [activeSymbol],
          price_lookback_days: 120,
          news_lookback_hours: 48,
          signal_horizon_bars: 5,
          mode: "live"
        };

        const res = await fetch("/research/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        setStepperStage("analytics");
        await new Promise(r => setTimeout(r, 40));
        setStepperStage("synthesis");

        if (!res.ok) {
          throw new Error("HTTP error " + res.status + ": " + (await res.text()));
        }

        const data = await res.json();
        currentRunId = data.run_id;
        const cleanSym = activeSymbol.toUpperCase().trim();
        const baseSym = cleanSym.split(".")[0].replace("^", "");
        currentReport = (data.reports && (
             data.reports[cleanSym] 
          || data.reports[baseSym] 
          || data.reports[cleanSym + ".NS"] 
          || data.reports[cleanSym.toLowerCase()]
          || Object.values(data.reports)[0]
        )) || null;

        setStepperStage("complete");
        if (!currentReport) {
          const errDetail = (data.errors && data.errors.length > 0) 
            ? data.errors.join("<br>") 
            : `No market quote or historical records found for symbol "${activeSymbol}".`;
          document.getElementById("reportContainer").innerHTML = `
            <div class="panel-card" style="border-color: var(--amber); margin-top: 24px;">
              <div class="panel-card-header">
                <div class="panel-title" style="color: var(--amber);">Stock Quote Notice: ${activeSymbol}</div>
                <div class="panel-pill" style="border-color: var(--amber); color: var(--amber);">Live Search</div>
              </div>
              <p style="color: var(--text-muted); margin-top: 12px; font-size: 0.95rem; line-height: 1.6;">
                ${errDetail}
              </p>
              <div style="margin-top: 16px; padding: 14px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                <strong style="color: var(--text);">Quick Indian Market Suggestions:</strong>
                <ul style="margin-left: 20px; margin-top: 8px; color: var(--text-muted); line-height: 1.6;">
                  <li>Search any <strong>NIFTY 50</strong> stock: <code>RELIANCE</code>, <code>TCS</code>, <code>HDFCBANK</code>, <code>INFY</code>, <code>ICICIBANK</code>, <code>BHARTIARTL</code>, <code>SBIN</code>, <code>LT</code>, <code>MARUTI</code>, <code>TATAPOWER</code></li>
                  <li>Search major indices: <code>NIFTY</code> (or <code>^NSEI</code>), <code>SENSEX</code> (or <code>^BSESN</code>)</li>
                  <li>Search any NSE/BSE ticker directly: e.g., <code>BEL.NS</code>, <code>HAL.NS</code>, <code>TMPV.NS</code>, <code>ETERNAL.NS</code></li>
                </ul>
              </div>
            </div>
          `;
          return;
        }

        renderReport(currentReport);
      } catch (err) {
        console.error(err);
        document.getElementById("reportContainer").innerHTML = `
          <div class="panel-card" style="border-color: var(--rose);">
            <h3 style="color: var(--rose);">Analysis Execution Error</h3>
            <p style="color: var(--text-muted); margin-top: 8px;">${err.message}</p>
          </div>
        `;
      } finally {
        btn.disabled = false;
        spinner.style.display = "none";
        btnText.innerText = "Run Research";
      }
    }

    function setStepperStage(stage) {
      const stages = ["init", "data", "analytics", "synthesis", "complete"];
      const idx = stages.indexOf(stage);
      stages.forEach((s, i) => {
        const el = document.getElementById("step-" + s);
        if (el) {
          el.className = "step-item " + (i < idx ? "completed" : (i === idx ? "active" : ""));
        }
      });
    }

    function getCompanyFullName(sym) {
      const clean = sym.toUpperCase().replace(".NS", "").replace(".BO", "").replace("^", "");
      const map = {
        "RELIANCE": "Reliance Industries Limited",
        "TCS": "Tata Consultancy Services Limited",
        "HDFCBANK": "HDFC Bank Limited",
        "ICICIBANK": "ICICI Bank Limited",
        "BHARTIARTL": "Bharti Airtel Limited",
        "INFY": "Infosys Limited",
        "ITC": "ITC Limited",
        "SBIN": "State Bank of India",
        "LT": "Larsen & Toubro Limited",
        "HINDUNILVR": "Hindustan Unilever Limited",
        "AXISBANK": "Axis Bank Limited",
        "KOTAKBANK": "Kotak Mahindra Bank Limited",
        "BAJFINANCE": "Bajaj Finance Limited",
        "MARUTI": "Maruti Suzuki India Limited",
        "M&M": "Mahindra & Mahindra Limited",
        "TITAN": "Titan Company Limited",
        "SUNPHARMA": "Sun Pharmaceutical Industries",
        "ADANIENT": "Adani Enterprises Limited",
        "TATAMOTORS": "Tata Motors Limited",
        "ULTRACEMCO": "UltraTech Cement Limited",
        "NTPC": "NTPC Limited",
        "ONGC": "Oil and Natural Gas Corporation",
        "POWERGRID": "Power Grid Corporation",
        "TATASTEEL": "Tata Steel Limited",
        "BAJAJFINSV": "Bajaj Finserv Limited",
        "COALINDIA": "Coal India Limited",
        "HCLTECH": "HCL Technologies Limited",
        "NESTLEIND": "Nestle India Limited",
        "ASIANPAINT": "Asian Paints Limited",
        "JSWSTEEL": "JSW Steel Limited",
        "GRASIM": "Grasim Industries Limited",
        "TECHM": "Tech Mahindra Limited",
        "HINDALCO": "Hindalco Industries Limited",
        "CIPLA": "Cipla Limited",
        "ADANIPORTS": "Adani Ports & SEZ Limited",
        "TRENT": "Trent Limited",
        "BEL": "Bharat Electronics Limited",
        "SHRIRAMFIN": "Shriram Finance Limited",
        "DRREDDY": "Dr. Reddy's Laboratories",
        "BPCL": "Bharat Petroleum Corporation",
        "EICHERMOT": "Eicher Motors Limited",
        "WIPRO": "Wipro Limited",
        "APOLLOHOSP": "Apollo Hospitals Enterprise",
        "HEROMOTOCO": "Hero MotoCorp Limited",
        "TATACONSUM": "Tata Consumer Products",
        "BRITANNIA": "Britannia Industries Limited",
        "SBILIFE": "SBI Life Insurance",
        "HDFCLIFE": "HDFC Life Insurance",
        "INDUSINDBK": "IndusInd Bank Limited",
        "DIVISLAB": "Divi's Laboratories Limited",
        "TATAPOWER": "Tata Power Company Limited",
        "JIOFIN": "Jio Financial Services",
        "ZOMATO": "Zomato Limited",
        "VEDL": "Vedanta Limited",
        "HAL": "Hindustan Aeronautics Limited",
        "NSEI": "NIFTY 50 Benchmark Index",
        "NIFTY": "NIFTY 50 Benchmark Index",
        "BSESN": "S&P BSE SENSEX 30 Index",
        "SENSEX": "S&P BSE SENSEX 30 Index",
      };
      return map[clean] || (sym.endsWith(".NS") || sym.endsWith(".BO") ? clean + " Limited" : sym);
    }

    function renderReport(rep) {
      if (!rep) return;

      const stateClass = rep.market_state === "BULLISH"
        ? "state-bullish"
        : (rep.market_state === "BEARISH" ? "state-bearish" : "state-neutral");

      const glowClass = rep.market_state === "BULLISH"
        ? "hero-glow-bullish"
        : (rep.market_state === "BEARISH" ? "hero-glow-bearish" : "hero-glow-neutral");

      const scoreColor = rep.signal_score >= 0.15 ? "#10b981" : (rep.signal_score <= -0.15 ? "#f43f5e" : "#f59e0b");
      const scorePct = Math.round(((rep.signal_score + 1.0) / 2.0) * 100);

      const snap = rep.snapshot;
      const tech = rep.technical;
      const sent = rep.sentiment;
      const sig = rep.signal;

      const isIndian = !rep.symbol.includes("AAPL") && !rep.symbol.includes("MSFT") && !rep.symbol.includes("NVDA") && !rep.symbol.includes("SPY");
      const curr = (rep.symbol.endsWith(".NS") || rep.symbol.endsWith(".BO") || rep.symbol.startsWith("^") || isIndian) ? "₹" : "$";

      const html = `
        <!-- Hero Section -->
        <div class="hero-card">
          <div class="${glowClass}"></div>
          <div class="hero-header">
            <div class="hero-symbol-group">
              <div>
                <div class="hero-symbol">${rep.symbol}</div>
                <div style="font-size: 0.92rem; color: var(--text-muted); font-weight: 600; margin-top: 3px;">
                  ${getCompanyFullName(rep.symbol)}
                </div>
              </div>
              <div class="state-pill ${stateClass}">
                ● ${rep.market_state}
              </div>
            </div>
            <div class="hero-meta">
              <div>Cutoff: <strong>${rep.analysis_timestamp.replace('T', ' ').substring(0, 19)} UTC</strong></div>
              <div>Run ID: <strong>${rep.run_id.substring(0, 8)}...</strong></div>
              <div>Freshness: <strong style="color:#10b981;">[FRESH] ${(snap.freshness_seconds/60).toFixed(1)}m</strong></div>
            </div>
          </div>

          <div class="hero-headline">${rep.headline}</div>
          <div class="hero-executive-box">
            ${rep.executive_summary}
          </div>

          <!-- Gauges Summary -->
          <div class="score-summary-grid">
            <div class="score-card">
              <div class="score-title">Quantitative Signal Score</div>
              <div class="score-val" style="color: ${scoreColor};">
                ${rep.signal_score >= 0 ? '+' : ''}${rep.signal_score.toFixed(2)}
              </div>
              <div class="score-bar-bg">
                <div class="score-bar-fill" style="width: ${scorePct}%; background: ${scoreColor};"></div>
              </div>
            </div>

            <div class="score-card">
              <div class="score-title">Signal Confidence</div>
              <div class="score-val" style="color: #6366f1;">
                ${(rep.confidence * 100).toFixed(1)}%
              </div>
              <div class="score-bar-bg">
                <div class="score-bar-fill" style="width: ${(rep.confidence * 100).toFixed(0)}%; background: #6366f1;"></div>
              </div>
            </div>

            <div class="score-card">
              <div class="score-title">Market Last Close</div>
              <div class="score-val">
                ${curr}${snap.price.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                <span style="font-size: 0.95rem; font-weight: 600; color: ${snap.change >= 0 ? '#10b981' : '#f43f5e'};">
                  ${snap.change >= 0 ? '+' : ''}${snap.change.toFixed(2)} (${snap.change_percent >= 0 ? '+' : ''}${snap.change_percent.toFixed(2)}%)
                </span>
              </div>
              <div class="score-bar-bg">
                <div class="score-bar-fill" style="width: 100%; background: ${snap.change >= 0 ? '#10b981' : '#f43f5e'};"></div>
              </div>
            </div>

            <div class="score-card">
              <div class="score-title">News Sentiment Score</div>
              <div class="score-val" style="color: ${sent.mean_score >= 0 ? '#10b981' : '#f43f5e'};">
                ${sent.mean_score >= 0 ? '+' : ''}${sent.mean_score.toFixed(2)}
              </div>
              <div class="score-bar-bg">
                <div class="score-bar-fill" style="width: ${Math.round(((sent.mean_score + 1)/2)*100)}%; background: #06b6d4;"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- View Switcher -->
        <div class="view-tabs">
          <button class="tab-btn active" onclick="switchView('visual')">Dashboard View</button>
          <button class="tab-btn" onclick="switchView('factors')">Factor Contributors</button>
          <button class="tab-btn" onclick="switchView('evidence')">Evidence & Provenance</button>
          <button class="tab-btn" onclick="switchView('markdown')">Markdown Report</button>
          <button class="tab-btn" onclick="switchView('json')">Raw JSON</button>
          <a href="/research/reports/${rep.run_id}/${rep.symbol}?format=html" target="_blank" class="tab-btn" style="text-decoration:none;">Open HTML &nearr;</a>
        </div>

        <!-- View 1: Visual Dashboard -->
        <div id="view-visual" class="tab-content">
          <div class="grid-3">
            <!-- Market Snapshot Panel -->
            <div class="panel-card">
              <div class="panel-card-header">
                <div class="panel-title">Market Snapshot</div>
                <div class="panel-pill">${snap.source}</div>
              </div>
              <div class="metric-list">
                <div class="metric-row">
                  <span class="metric-name">Open Price</span>
                  <span class="metric-num">${curr}${snap.open.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">Day High</span>
                  <span class="metric-num">${curr}${snap.high.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">Day Low</span>
                  <span class="metric-num">${curr}${snap.low.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">Trading Volume</span>
                  <span class="metric-num">${snap.volume.toLocaleString()}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">Data Freshness</span>
                  <span class="metric-num" style="color: #10b981;">${(snap.freshness_seconds / 60).toFixed(1)} mins</span>
                </div>
              </div>
            </div>

            <!-- Technical Indicators Panel -->
            <div class="panel-card">
              <div class="panel-card-header">
                <div class="panel-title">Technical Indicators</div>
                <div class="panel-pill">Point-in-Time</div>
              </div>
              <div class="metric-list">
                <div class="metric-row">
                  <span class="metric-name">SMA (20 / 50)</span>
                  <span class="metric-num">${tech.sma_20 ? tech.sma_20.toFixed(2) : 'N/A'} / ${tech.sma_50 ? tech.sma_50.toFixed(2) : 'N/A'}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">EMA (20)</span>
                  <span class="metric-num">${tech.ema_20 ? tech.ema_20.toFixed(2) : 'N/A'}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">RSI (14)</span>
                  <span class="metric-num" style="color: ${tech.rsi_14 > 70 ? '#f43f5e' : (tech.rsi_14 < 30 ? '#10b981' : '#38bdf8')};">
                    ${tech.rsi_14 ? tech.rsi_14.toFixed(1) : 'N/A'}
                    <span class="metric-sub">${tech.rsi_14 > 70 ? '(Overbought)' : (tech.rsi_14 < 30 ? '(Oversold)' : '(Neutral)')}</span>
                  </span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">MACD / Signal</span>
                  <span class="metric-num">${tech.macd ? tech.macd.toFixed(2) : 'N/A'} / ${tech.macd_signal ? tech.macd_signal.toFixed(2) : 'N/A'}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">ATR (14)</span>
                  <span class="metric-num">${curr}${tech.atr_14 ? tech.atr_14.toFixed(2) : 'N/A'}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">Realized Volatility (20d)</span>
                  <span class="metric-num">${tech.realized_volatility_20 ? (tech.realized_volatility_20 * 100).toFixed(1) + '%' : 'N/A'}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">Volume Z-Score</span>
                  <span class="metric-num">${tech.volume_zscore_20 ? tech.volume_zscore_20.toFixed(2) : 'N/A'}</span>
                </div>
              </div>
            </div>

            <!-- Sentiment & News Panel -->
            <div class="panel-card">
              <div class="panel-card-header">
                <div class="panel-title">News Sentiment</div>
                <div class="panel-pill">${sent.article_count} Articles</div>
              </div>
              <div class="metric-list" style="margin-bottom: 16px;">
                <div class="metric-row">
                  <span class="metric-name">Positive / Negative Ratio</span>
                  <span class="metric-num">${(sent.positive_share * 100).toFixed(0)}% / ${(sent.negative_share * 100).toFixed(0)}%</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">Source Diversity</span>
                  <span class="metric-num">${sent.source_diversity} Publishers</span>
                </div>
              </div>
              <div class="news-list">
                ${(rep.top_news || []).slice(0, 3).map(art => {
                  const sLabel = art.sentiment ? art.sentiment.label.toUpperCase() : 'NEUTRAL';
                  const sScore = art.sentiment ? art.sentiment.score.toFixed(2) : '0.00';
                  const color = sLabel === 'POSITIVE' ? '#10b981' : (sLabel === 'NEGATIVE' ? '#f43f5e' : '#f59e0b');
                  return `
                    <div class="news-item">
                      <a href="${art.article_url}" target="_blank" class="news-title">${art.title}</a>
                      <div class="news-meta">
                        <span>${art.publisher}</span>
                        <span class="news-sent-tag" style="background: rgba(255,255,255,0.06); color: ${color};">${sLabel} (${sScore >= 0 ? '+' : ''}${sScore})</span>
                      </div>
                    </div>
                  `;
                }).join('')}
              </div>
            </div>
          </div>

          <!-- Scenario Analysis -->
          <div class="panel-card" style="margin-bottom: 24px;">
            <div class="panel-card-header">
              <div class="panel-title">Scenario Analysis</div>
              <div class="panel-pill">5-Day Horizon</div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
              ${Object.entries(rep.scenario_analysis || {}).map(([key, val]) => `
                <div style="background: rgba(0,0,0,0.25); border: 1px solid var(--card-border); border-radius: 10px; padding: 16px;">
                  <div style="font-size: 0.8rem; font-weight: 700; color: #818cf8; text-transform: uppercase; margin-bottom: 6px;">
                    ${key.replace('_', ' ')}
                  </div>
                  <div style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.5;">${curr === '₹' ? val.replaceAll('$', '₹') : val}</div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>

        <!-- View 2: Factors Breakdown -->
        <div id="view-factors" class="tab-content" style="display: none;">
          <div class="panel-card">
            <div class="panel-card-header">
              <div class="panel-title">Multi-Factor Quantitative Contributors</div>
              <div class="panel-pill">${sig.method} &bull; ${sig.model_version}</div>
            </div>
            <table class="factors-table">
              <thead>
                <tr>
                  <th>Factor Name</th>
                  <th>Weight</th>
                  <th>Normalized Value</th>
                  <th>Contribution</th>
                  <th>Direction</th>
                </tr>
              </thead>
              <tbody>
                ${(sig.top_contributors || []).map(c => `
                  <tr>
                    <td style="color: #f1f5f9; font-weight: 600; text-transform: capitalize;">${c.name}</td>
                    <td>${c.weight.toFixed(2)}</td>
                    <td style="color: ${c.value >= 0 ? '#10b981' : '#f43f5e'};">${c.value >= 0 ? '+' : ''}${c.value.toFixed(2)}</td>
                    <td>
                      <div class="factor-bar-container">
                        <div style="width: ${Math.min(100, Math.abs(c.contribution) * 200)}%; height: 100%; background: ${c.contribution >= 0 ? '#10b981' : '#f43f5e'};"></div>
                      </div>
                      ${c.contribution >= 0 ? '+' : ''}${c.contribution.toFixed(3)}
                    </td>
                    <td><span style="color: ${c.direction === 'BULLISH' ? '#10b981' : (c.direction === 'BEARISH' ? '#f43f5e' : '#f59e0b')}; font-weight: 700;">${c.direction}</span></td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>

        <!-- View 3: Evidence & Audit -->
        <div id="view-evidence" class="tab-content" style="display: none;">
          <div class="panel-card">
            <div class="panel-card-header">
              <div class="panel-title">Evidence & Provenance Binding (Rule 5 Audit Chain)</div>
              <div class="panel-pill">Point-in-Time Enforced</div>
            </div>
            <table class="evidence-table">
              <thead>
                <tr>
                  <th>Claim ID</th>
                  <th>Claim Narrative</th>
                  <th>Evidence Type</th>
                  <th>Reference & Provenance</th>
                </tr>
              </thead>
              <tbody>
                ${(rep.evidence || []).map(ev => `
                  <tr>
                    <td class="claim-tag">${ev.claim_id}</td>
                    <td style="color: #e2e8f0;">${ev.claim_text}</td>
                    <td><code>${ev.evidence_type}</code></td>
                    <td>
                      ${ev.source_url ? `<a href="${ev.source_url}" target="_blank" style="color: #38bdf8;">${ev.evidence_ref}</a>` : `<code>${ev.evidence_ref}</code>`}
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>

        <!-- View 4: Markdown View -->
        <div id="view-markdown" class="tab-content" style="display: none;">
          <div class="panel-card">
            <div class="panel-card-header">
              <div class="panel-title">Markdown Representation</div>
              <button class="btn-secondary" onclick="copyMarkdown()">Copy to Clipboard</button>
            </div>
            <pre id="mdContent" class="code-view">Loading Markdown...</pre>
          </div>
        </div>

        <!-- View 5: JSON View -->
        <div id="view-json" class="tab-content" style="display: none;">
          <div class="panel-card">
            <div class="panel-card-header">
              <div class="panel-title">Raw JSON Contract</div>
              <button class="btn-secondary" onclick="copyJSON()">Copy JSON</button>
            </div>
            <pre id="jsonContent" class="code-view">${escapeHtml(JSON.stringify(rep, null, 2))}</pre>
          </div>
        </div>
      `;

      document.getElementById("reportContainer").innerHTML = html;
    }

    function switchView(tabId) {
      document.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.toggle("active", b.innerText.toLowerCase().includes(tabId));
      });
      document.querySelectorAll(".tab-content").forEach(el => el.style.display = "none");
      const target = document.getElementById("view-" + tabId);
      if (target) target.style.display = "block";

      if (tabId === "markdown" && currentRunId && activeSymbol) {
        fetch(`/research/reports/${currentRunId}/${activeSymbol}?format=markdown`)
          .then(r => r.text())
          .then(txt => {
            document.getElementById("mdContent").innerText = txt;
          });
      }
    }

    function copyMarkdown() {
      const txt = document.getElementById("mdContent").innerText;
      navigator.clipboard.writeText(txt);
      alert("Markdown report copied to clipboard!");
    }

    function copyJSON() {
      const txt = document.getElementById("jsonContent").innerText;
      navigator.clipboard.writeText(txt);
      alert("JSON payload copied to clipboard!");
    }

    function escapeHtml(str) {
      return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    // Auto-load RELIANCE analysis on initial page load
    window.addEventListener("DOMContentLoaded", () => {
      runAnalysis();
    });
  </script>
</body>
</html>
"""
