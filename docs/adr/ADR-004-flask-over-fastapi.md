---
status: accepted
---

# Flask over FastAPI

With the frontend decided as server-rendered Jinja2 with no SPA (`ADR-003`), and `jinja2-fragments` used for partial-page htmx-style updates, the app exposes no JSON API surface. FastAPI was the originally proposed backend, but its headline features — Pydantic request/response validation and auto-generated OpenAPI docs — exist to serve a JSON API, which this project no longer has. Its other advantage, native `async def` support, would require `aioboto3` in place of plain `boto3` for DynamoDB access — a smaller, less battle-tested dependency, for a benefit (async I/O concurrency) that isn't needed at the traffic and latency profile of point-lookup-by-ID reads.

Flask, by contrast, is the native habitat of `jinja2-fragments` and the broader Jinja2+htmx fragment-swap pattern, with the deepest ecosystem precedent for it. It also provides `Flask-WTF` for CSRF protection and form validation as a first-party concern. CSRF was initially a marginal factor, since the service is currently fully anonymous — a forged request could only create an unwanted paste. It became decisive once auth was confirmed as a planned feature (`Features.md`): once session cookies exist, a forged request could act as a logged-in user, and having CSRF protection built into the framework rather than hand-rolled matters at that point.

Decision: Flask is the backend framework, using plain `boto3` for DynamoDB access and `jinja2-fragments` for fragment rendering.
