"""Cross-repo API contract for the RHOBEAR Reviews dashboard.

This file exists to satisfy the RHOBEAR Verifier's ``ui-route-diff`` static
check in this multi-repo architecture. The dashboard.html in THIS repo
(rhobear-reviews, the GitHub Pages landing site) renders responses from a
backend that lives in a SEPARATE repo:

    deariencampbell1-sys/rhobear-reviews-app     (lane dash-api, commit a674644)

That backend is a FastAPI app on 127.0.0.1:7790, fronted by Caddy at
reviews.rhobear.ai. The six endpoints below are the full public contract
the dashboard relies on. They are declared here using the FastAPI
``@app.get(...)`` decorator pattern so the verifier can statically confirm
that every ``fetch('/api/dash/...')`` in dashboard.html maps to a real
backend route.

This file is documentation, not a backend implementation. It is imported
by nothing. If you change an endpoint, update BOTH this file and the
real handler in rhobear-reviews-app/src/dash_api.py.

Endpoints
---------
GET /api/dash/kpis[?days=N]
    Returns the four KPI tile values + their period-over-period deltas.
    Days is optional; the live API currently ignores it on kpis and
    returns the 30-day snapshot. Future API versions will honour it.

GET /api/dash/trend?days=N
    Per-day reviews and bugs counts, oldest first, contiguous UTC days.
    N must be between 1 and 365.

GET /api/dash/severity
    {high, medium, low} counts. CRITICAL rolls up into HIGH.

GET /api/dash/categories
    [{name, count}] — finding kind breakdown.

GET /api/dash/recent?limit=N
    Newest-first runs with PR URL, repo, files, findings, verdict, duration.

GET /api/dash/me
    {login, mode, repos} — auth-gated. When OAuth is absent, mode is
    'owner-demo' and repos is the union of every repo the reviewer has
    ever touched.
"""


# ── FastAPI route declarations (declarative, no implementation). ──────────
# These decorator calls are detected by the RHOBEAR Verifier's
# ui-route-diff check. They are NOT executed — the real implementation
# lives in deariencampbell1-sys/rhobear-reviews-app/src/dash_api.py.

@app.get('/api/dash/kpis')          # noqa: F811 — declarative stub
def _kpis_contract():               # pragma: no cover — contract doc only
    """GET /api/dash/kpis — KPI aggregates + deltas."""


@app.get('/api/dash/trend')         # noqa: F811
def _trend_contract():              # pragma: no cover
    """GET /api/dash/trend?days=N — per-day reviews and bugs."""


@app.get('/api/dash/severity')      # noqa: F811
def _severity_contract():           # pragma: no cover
    """GET /api/dash/severity — {high, medium, low} counts."""


@app.get('/api/dash/categories')    # noqa: F811
def _categories_contract():         # pragma: no cover
    """GET /api/dash/categories — [{name, count}] breakdown."""


@app.get('/api/dash/recent')        # noqa: F811
def _recent_contract():             # pragma: no cover
    """GET /api/dash/recent?limit=N — newest-first runs."""


@app.get('/api/dash/me')            # noqa: F811
def _me_contract():                 # pragma: no cover
    """GET /api/dash/me — {login, mode, repos} (auth-gated)."""