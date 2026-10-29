import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
from src.db import Database
from src.analytics import AnalyticsEngine

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AI Finance Tracker — Dashboard</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }
    .container { max-width: 1000px; margin: 0 auto; }
    h1 { color: #38bdf8; margin-bottom: 0.5rem; }
    .subtitle { color: #94a3b8; margin-bottom: 2rem; }
    .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
    .card { background: #1e293b; padding: 1.5rem; border-radius: 8px; border: 1px solid #334155; }
    .card-title { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; }
    .card-val { font-size: 1.8rem; font-weight: bold; margin-top: 0.5rem; }
    .green { color: #34d399; }
    .red { color: #f87171; }
    table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; margin-top: 1rem; }
    th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #334155; }
    th { background: #0f172a; color: #94a3b8; }
  </style>
</head>
<body>
  <div class="container">
    <h1>AI Finance Tracker</h1>
    <div class="subtitle">100% Local-First &bull; SQLite &bull; Zero Bank Credentials Required &bull; Vecesta.co</div>
    <div id="cards" class="cards">
      <div class="card"><div class="card-title">Total Income</div><div id="inc" class="card-val green">Loading...</div></div>
      <div class="card"><div class="card-title">Total Expenses</div><div id="exp" class="card-val red">Loading...</div></div>
      <div class="card"><div class="card-title">Net Savings</div><div id="net" class="card-val">Loading...</div></div>
      <div class="card"><div class="card-title">Savings Rate</div><div id="rate" class="card-val">Loading...</div></div>
    </div>
    <h2>Recent Transactions</h2>
    <table id="txTable">
      <thead><tr><th>Date</th><th>Payee</th><th>Category</th><th>Amount</th></tr></thead>
      <tbody></tbody>
    </table>
  </div>
  <script>
    fetch('/api/summary').then(r=>r.json()).then(d=>{
      document.getElementById('inc').innerText = '+$' + d.total_income.toLocaleString();
      document.getElementById('exp').innerText = '-$' + d.total_expenses.toLocaleString();
      document.getElementById('net').innerText = '$' + d.net_savings.toLocaleString();
      document.getElementById('rate').innerText = d.savings_rate + '%';
    });
    fetch('/api/transactions').then(r=>r.json()).then(txs=>{
      const tb = document.querySelector('#txTable tbody');
      txs.slice(0, 15).forEach(t=>{
        const tr = document.createElement('tr');
        const color = t.amount < 0 ? 'color: #f87171;' : 'color: #34d399;';
        tr.innerHTML = `<td>${t.date}</td><td>${t.payee}</td><td>${t.category}</td><td style="${color}">${t.amount < 0 ? '-$' : '+$'}${Math.abs(t.amount).toFixed(2)}</td>`;
        tb.appendChild(tr);
      });
    });
  </script>
</body>
</html>
"""

class FinanceHTTPHandler(BaseHTTPRequestHandler):
    db: Database = None

    def _send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        if self.path in ("/", "/dashboard"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))

        elif self.path == "/api/transactions":
            txs = self.db.get_all_transactions()
            self._send_json(200, [t.model_dump() for t in txs])

        elif self.path == "/api/summary":
            txs = self.db.get_all_transactions()
            summary = AnalyticsEngine.summarize_cashflow(txs)
            self._send_json(200, summary.model_dump())

        elif self.path == "/api/subscriptions":
            txs = self.db.get_all_transactions()
            subs = AnalyticsEngine.detect_subscriptions(txs)
            self._send_json(200, [s.model_dump() for s in subs])

        elif self.path == "/api/anomalies":
            txs = self.db.get_all_transactions()
            anomalies = AnalyticsEngine.detect_anomalies(txs)
            self._send_json(200, [a.model_dump() for a in anomalies])

        elif self.path == "/health":
            self._send_json(200, {"status": "ok", "service": "ai-finance-tracker"})

        else:
            self._send_json(404, {"error": "Not found"})

    def log_message(self, format, *args):
        pass

def run_server(db: Optional[Database] = None, host: str = "127.0.0.1", port: int = 5000, background: bool = False) -> HTTPServer:
    database = db or Database("finance.db")
    handler = FinanceHTTPHandler
    handler.db = database
    server = HTTPServer((host, port), handler)

    if background:
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        return server
    else:
        print(f"AI Finance Tracker Dashboard running at http://{host}:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down dashboard...")
            server.shutdown()
        return server
