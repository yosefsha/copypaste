# Tasks

Step-by-step implementation plan derived from the decisions in `docs/adr/`. Organized in build order — each phase assumes the previous one is done. Check items off as they're completed.

## 0. Open decision to confirm before starting

- [x] Confirm the paste content size cap (380KB was proposed, driven by DynamoDB's 400KB item limit — `ADR-002`) — confirmed: 380KB (388,096 bytes).

## 1. Repo scaffolding

- [x] Choose Python dependency/build tool (e.g. `uv`, `poetry`, or plain `venv`+`pip`) and initialize project metadata (`pyproject.toml`). — `uv`
- [x] Add Flask, `boto3`, `jinja2-fragments`, `Flask-WTF` as dependencies (`ADR-004`).
- [x] Add `Dockerfile` for the Flask app.
- [x] Add `docker-compose.yml` wiring the app service to `amazon/dynamodb-local` on a shared network, addressed by service name (`ADR-002`).
- [x] Add a `.env`/config mechanism for a configurable DynamoDB endpoint (local vs AWS) (`ADR-002`). — `DYNAMODB_ENDPOINT_URL` in `src/copypaste/config.py`
- [x] Update `CLAUDE.md` with real build/run/test commands once tooling is chosen (per its own "Status" instructions).

## 2. Data layer

- [x] Define the DynamoDB table schema for Paste: partition key `paste_id`, attribute for content, created-at timestamp; consider a TTL attribute placeholder for future expiry (`ADR-002`). — no TTL attribute added yet (no expiry feature exists to use it); schema is `paste_id` (PK), `content`, `created_at`.
- [x] Write a table-creation script/module usable against both DynamoDB Local and real DynamoDB (same code path, different endpoint) (`ADR-002`). — `src/copypaste/db.py::create_table`, idempotent.
- [x] Implement base62 7-character random ID generation (`ADR-001`). — `src/copypaste/ids.py`.
- [x] Implement collision-checked write: `PutItem` with `attribute_not_exists(paste_id)` condition expression, retry with a new random ID on `ConditionalCheckFailedException` (`ADR-001`). — `src/copypaste/db.py::put_paste`.
- [x] Implement `get_paste(paste_id)` point-read by ID.
- [x] Enforce the paste size cap on write, rejecting oversized submissions before hitting DynamoDB's item limit (`ADR-002`, see open decision above). — 380KB, `db.PasteTooLargeError`.

## 3. Web layer (Flask, `ADR-003`, `ADR-004`)

- [x] Scaffold the Flask app factory and blueprint(s). — single `create_app()` factory in `src/copypaste/app.py`; no blueprints yet (only 3 routes, would be premature).
- [x] Build the create-paste flow: GET form route + Jinja2 template, POST route that validates input, calls the data layer, and redirects to the new paste's view URL.
- [x] Wire `Flask-WTF` CSRF protection on the create form.
- [x] Build the view-paste flow: GET route by `paste_id`, Jinja2 template rendering the raw text plus Open Graph meta tags for link unfurling (`ADR-003`).
- [x] Handle not-found IDs (404 page).
- [x] Set `Cache-Control: public, max-age=31536000, immutable` on the view route response.
- [ ] Add any partial-update interactions (e.g. copy-to-clipboard feedback) via `jinja2-fragments` + htmx rather than full page reloads. — deferred, UI polish, not part of this vertical slice.

## 4. Testing (`ADR-002`)

- [x] Unit tests for ID generation, collision retry logic, and size-cap validation using `moto` to mock DynamoDB. — done as part of task 2/3 (`tests/unit/`).
- [x] Integration tests for create/view flows running against `amazon/dynamodb-local` inside the Compose network. — `tests/integration/`, fresh table created/deleted per test.
- [x] Wire both test tiers into a single test-runner command, documented in `CLAUDE.md`. — `docker compose run --rm app pytest` (bare, no path) discovers and runs both.

## 3b. Pastebin-parity metadata & polish (`ADR-006`)

- [ ] Add optional `title` field: `db.py` `Paste` dataclass return type + `put_paste`/`get_paste` support, `forms.py` field, view rendering (`step/paste-title`).
- [ ] Add optional expiration via DynamoDB TTL on `expires_at`: table TTL setup, `put_paste` support, expiry check in `get_paste`, form select (`step/paste-expiration`).
- [ ] Add optional syntax highlighting via Pygments: `language` field, curated language `<select>`, server-rendered highlighted view with plain-`<pre>` fallback (`step/syntax-highlighting`).
- [ ] Add `/raw/<paste_id>` plaintext route and a vanilla-JS copy-to-clipboard button on the view page (`step/copy-to-clipboard-raw-view`).
- [ ] Dark, pastebin-style visual theme for create/view/404 templates via a plain CSS file (`step/visual-polish`).

## 5. Static assets & CDN

- [ ] Identify static assets (CSS, any JS for htmx/copy button) and decide their build/bundling approach. — decided: plain CSS via Flask's default static folder, vanilla JS for copy-to-clipboard, no bundler (see phase 3b).
- [ ] Provision an S3 bucket for static assets, served via CloudFront.
- [ ] Provision the CloudFront distribution's second origin/behavior for dynamic routes (create, view, htmx fragments), pointed at the ALB (`ADR-005`).

## 6. Compute & networking (`ADR-005`)

- [ ] Write the ECS Fargate task definition for the Flask app (container image, gunicorn entrypoint, env vars for DynamoDB endpoint/region).
- [ ] Provision the ECS service/cluster.
- [ ] Provision the Application Load Balancer in front of the Fargate service, with health checks against a `/healthz` route.
- [ ] Point CloudFront's non-static-route origin at the ALB.

## 7. Abuse prevention

- [ ] Create an AWS WAF Web ACL with a rate-based rule on the create route, attached to the CloudFront distribution.

## 8. Deployment / CI

- [ ] Set up CI to run unit + integration tests on every push.
- [ ] Set up build/push of the container image to a registry (e.g. ECR).
- [ ] Set up deployment of infra (IaC tool TBD — not yet chosen) and app releases to Fargate.

## Deferred (see `Features.md`)

Not part of this plan — explicitly out of scope until their own future pass: mutability, S3 fallback for oversized pastes, auth/accounts.
