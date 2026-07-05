# Features

Planned features that are explicitly out of scope for now, kept here so today's scope decisions don't accidentally foreclose them.

## Mutability

Pastes are currently immutable / write-once (see `CONTEXT.md`, `ADR-001`, `ADR-003`). A future version will allow editing a paste's content in place. This is expected to touch:
- Cache-Control on the view route — currently `immutable`, will need to move to revalidation or explicit CloudFront invalidation on edit for pastes that support editing.
- The edit flow itself is expected to be a plain server-rendered form-and-redirect, consistent with the Jinja2-only frontend (`ADR-003`).
- ID generation is already random rather than content-derived specifically so identity stays stable across edits (`ADR-001`).

## S3 fallback for oversized pastes

Pastes over the size limit are currently rejected outright, driven by DynamoDB's 400KB item size limit (`ADR-002`). A future version could store oversized paste bodies in S3 instead, with DynamoDB holding only metadata plus a pointer to the S3 object, removing the size cap for large pastes.

## Static assets via S3 + CloudFront

Static assets (`style.css`, `pygments.css`) are currently served directly by Flask from
`src/copypaste/static/`, its default static folder — sufficient at current scale. A future version
could provision an S3 bucket for these assets and a CloudFront distribution with two
origins/behaviors: S3 for static paths, the ALB (`ADR-005`) for dynamic routes (create, view, htmx
fragments). This is expected to touch:
- A deploy-time sync step (CI, `TASKS.md` phase 8) to push `src/copypaste/static/*` to S3 — the
  files stay authored under `src/`; only the serving path changes in production.

## Auth

The service is currently fully anonymous — no accounts, no sessions. A future version will add user accounts. This is expected to touch:
- CSRF protection becomes a real concern once session cookies exist (a forged request could act as a logged-in user), which is part of why Flask/Flask-WTF was chosen over FastAPI (`ADR-004`).
- A future Users concept in DynamoDB, and a "my pastes" listing, neither of which exist in the current schema.
- Per-paste ownership, which is a prerequisite for anything that means "only the owner can see/manage this": private/unlisted exposure levels (pastebin.com's "Paste Exposure" setting), folders for organizing a user's own pastes, and a public "my pastes" archive listing. None of these exist today; unlike title/expiration/syntax-highlighting (`ADR-006`), they're attributes of a *relationship between a user and a paste*, not of the paste alone, so they wait for accounts.
