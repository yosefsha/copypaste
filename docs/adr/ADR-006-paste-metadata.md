---
status: accepted
---

# Optional anonymous paste metadata: title, expiration, syntax highlighting

Comparing copypaste against pastebin.com surfaced a large surface area of features, most of which depend on accounts (private/public exposure, folders, a "my pastes" archive) and are explicitly deferred (`Features.md`). Three fields stood out as different in kind: title, expiration, and syntax-highlighting language are all attributes of a single anonymous Paste, not of a user, so they don't require solving auth first.

**Title.** An optional, plain string (max 255 characters) stored as the `title` attribute, omitted from the item entirely when blank rather than stored as an empty string — DynamoDB items shouldn't carry attributes with no information. Displayed as the page heading and in `<title>`/Open Graph tags, falling back to the paste ID when absent.

**Expiration.** DynamoDB's native TTL attribute was already flagged in `ADR-002` as a "free option if expiring pastes are added later" — this is that later. Expiration is stored as `expires_at` (epoch seconds), omitted when the user selects "Never". The table enables TTL on `expires_at` via `update_time_to_live`, which is safe to call repeatedly (DynamoDB rejects re-enabling an identical spec with a `ValidationException`, which is swallowed). DynamoDB's TTL sweep is best-effort and can lag up to 48 hours past the actual expiry time, so it cannot be relied on alone for read-time correctness: `get_paste` independently compares `expires_at` to the current time and treats an expired-but-not-yet-reaped item as not-found, the same as a truly deleted one.

**Syntax highlighting.** Rendered server-side with Pygments rather than a client-side JS highlighter (e.g. highlight.js). `ADR-003` chose server-rendered Jinja2 specifically so paste content is visible to non-JS HTTP clients (link-unfurling scrapers) and so the app stays a single Python runtime with no separate frontend build step; a client-side highlighter would still leave the raw, unhighlighted text as what non-JS clients see, and would need a bundling story `ADR-003` deliberately avoided. Pygments runs entirely at render time and produces plain HTML/CSS, so it fits the existing SSR model with no new runtime and no build tooling. The `language` attribute stores a Pygments lexer alias from a curated `<select>` list (not free text, to avoid passing arbitrary lexer names to Pygments); absent or `"text"` falls back to a plain `<pre>` block.

Decision: add `title`, `expires_at`, and `language` as optional attributes on the existing Paste item, none of which require an account or ownership concept. `get_paste` returns a small `Paste` value object carrying these fields (replacing its previous bare `content: str | None` return) so callers can render all three together.
