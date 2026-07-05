# Tasks

Step-by-step implementation plan derived from the decisions in `docs/adr/`. Organized in build order — each phase assumes the previous one is done. Check items off as they're completed.

## 0. Open decision to confirm before starting

- [ ] Confirm the paste content size cap (380KB was proposed, driven by DynamoDB's 400KB item limit — `ADR-002`) — not yet formally confirmed.

## 1. Repo scaffolding

- [ ] Choose Python dependency/build tool (e.g. `uv`, `poetry`, or plain `venv`+`pip`) and initialize project metadata (`pyproject.toml`).
- [ ] Add Flask, `boto3`, `jinja2-fragments`, `Flask-WTF` as dependencies (`ADR-004`).
- [ ] Add `Dockerfile` for the Flask app.
- [ ] Add `docker-compose.yml` wiring the app service to `amazon/dynamodb-local` on a shared network, addressed by service name (`ADR-002`).
- [ ] Add a `.env`/config mechanism for a configurable DynamoDB endpoint (local vs AWS) (`ADR-002`).
- [ ] Update `CLAUDE.md` with real build/run/test commands once tooling is chosen (per its own "Status" instructions).

## 2. Data layer

- [ ] Define the DynamoDB table schema for Paste: partition key `paste_id`, attribute for content, created-at timestamp; consider a TTL attribute placeholder for future expiry (`ADR-002`).
- [ ] Write a table-creation script/module usable against both DynamoDB Local and real DynamoDB (same code path, different endpoint) (`ADR-002`).
- [ ] Implement base62 7-character random ID generation (`ADR-001`).
- [ ] Implement collision-checked write: `PutItem` with `attribute_not_exists(paste_id)` condition expression, retry with a new random ID on `ConditionalCheckFailedException` (`ADR-001`).
- [ ] Implement `get_paste(paste_id)` point-read by ID.
- [ ] Enforce the paste size cap on write, rejecting oversized submissions before hitting DynamoDB's item limit (`ADR-002`, see open decision above).

## 3. Web layer (Flask, `ADR-003`, `ADR-004`)

- [ ] Scaffold the Flask app factory and blueprint(s).
- [ ] Build the create-paste flow: GET form route + Jinja2 template, POST route that validates input, calls the data layer, and redirects to the new paste's view URL.
- [ ] Wire `Flask-WTF` CSRF protection on the create form.
- [ ] Build the view-paste flow: GET route by `paste_id`, Jinja2 template rendering the raw text plus Open Graph meta tags for link unfurling (`ADR-003`).
- [ ] Handle not-found IDs (404 page).
- [ ] Set `Cache-Control: public, max-age=31536000, immutable` on the view route response.
- [ ] Add any partial-update interactions (e.g. copy-to-clipboard feedback) via `jinja2-fragments` + htmx rather than full page reloads.

## 4. Testing (`ADR-002`)

- [ ] Unit tests for ID generation, collision retry logic, and size-cap validation using `moto` to mock DynamoDB.
- [ ] Integration tests for create/view flows running against `amazon/dynamodb-local` inside the Compose network.
- [ ] Wire both test tiers into a single test-runner command, documented in `CLAUDE.md`.

## 5. Static assets & CDN

- [ ] Identify static assets (CSS, any JS for htmx/copy button) and decide their build/bundling approach.
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
