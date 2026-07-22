# Deploy: reviews.rhobear.ai — landing at `/`, dashboard at `/dashboard/`

**Audience:** the dispatcher (only the dispatcher touches the VPS).
**Scope of this lane:** this repo (`rhobear-reviews`) prepared the landing,
the funnel links, the contract docstring, the Caddy proposal
(`deploy/caddy-reviews.txt`), and this runbook. Nothing here has been deployed.

## What changes

Today the whole origin is reverse-proxied to Cloud Run, so `/` serves the
**dashboard** and the landing page is served **nowhere** (`/landing.html` 404s).

After this deploy:

| Path            | Served by                                       |
|-----------------|-------------------------------------------------|
| `/`             | landing page (static docroot)                   |
| `/assets/*`     | landing's own assets (static docroot)           |
| `/dashboard/`   | Cloud Run `rhobear-reviews-dash` (prefix stripped) |
| `/dashboard/*`  | Cloud Run (dashboard app + its relative assets) |
| `/api/dash/*`   | Cloud Run (dashboard API, path intact)          |
| `/webhook`      | local bot receiver `127.0.0.1:8766` (unchanged) |

## Steps (on rhobear-vps, as the Caddy-running user)

### 1. Stage the landing docroot

```sh
ssh rhobear-vps
sudo mkdir -p /var/www/rhobear-reviews-landing
sudo chown -R "$USER":"$USER" /var/www/rhobear-reviews-landing
```

### 2. Copy the landing files up (from this repo's checkout)

Run these from the repo root on your local box (the Windows side), not on the
VPS. Only two things ship: `index.html` and the `assets/` directory.

```sh
scp index.html rhobear-vps:/var/www/rhobear-reviews-landing/index.html
scp -r assets rhobear-vps:/var/www/rhobear-reviews-landing/assets
```

> The stale `dashboard.html` that still lives in this repo is **not** deployed
> — the live dashboard is the Cloud Run app. Leave it; decide its fate at merge.

### 3. Swap the Caddy vhost

Open the live Caddyfile, find the `reviews.rhobear.ai { ... }` block, and
replace it verbatim with the contents of `deploy/caddy-reviews.txt`. Two
substitutions are required:

- Every `<HASH>` → the current Cloud Run revision URL that is **already in the
  live block** (form: `rhobear-reviews-dash-<HASH>.us-central1.run.app`).
  Reuse the identical string for both `/dashboard/*` and `/api/dash/*`.
- Confirm `/var/www/rhobear-reviews-landing` is the path you created in step 1.

### 4. Validate, then reload

```sh
caddy validate --config /etc/caddy/Caddyfile      # path per your install
sudo systemctl reload caddy                        # zero-downtime reload
```

If `validate` errors, **do not reload** — Caddy keeps serving the old config.
The most likely error is a malformed matcher or a missing `<HASH>` token.

## Verification (drive it like a user — not just curl)

Do every one of these after the reload. A green `validate` is not acceptance.

1. **Landing at root.** `curl -sI https://reviews.rhobear.ai/` → `200`, and the
   body contains a landing-only string, e.g.
   `curl -s https://reviews.rhobear.ai/ | grep -o 'Senior-grade AI code review'`.
   It must NOT be the dashboard.
2. **Landing asset.** `curl -sI https://reviews.rhobear.ai/assets/rhobear-logo.png`
   → `200` and `content-type: image/png` (proves the docroot, not the proxy).
3. **Dashboard renders.** Open `https://reviews.rhobear.ai/dashboard/` in a
   browser. The KPI tiles must populate with real numbers (not 0 / not an error
   banner). Also try `/dashboard` (no slash) — it should redirect and load.
4. **Dashboard API through the origin.**
   `curl -sI https://reviews.rhobear.ai/api/dash/kpis` → `200` (JSON) or an
   auth-gated response — **never** `502`/`503`/`504`. Repeat for `/api/dash/trend`.
5. **Webhook unchanged.** `curl -sI https://reviews.rhobear.ai/webhook` → `200`
   or `405` (method-gated). A `502` means the receiver on `:8766` is down.
6. **No cross-contamination.** `https://reviews.rhobear.ai/dashboard/` is the
   dashboard; `https://reviews.rhobear.ai/` is the landing. Confirm a dashboard
   asset loads, e.g. open devtools and check a `/dashboard/assets/*` request
   returns `200` (proves the prefix strip, step 3 covers this visually).

## Rollback

Revert the Caddyfile's `reviews.rhobear.ai` block to the previous (single
catch-all proxy) form and `sudo systemctl reload caddy`. The landing docroot can
stay; it simply becomes unreachable again.
