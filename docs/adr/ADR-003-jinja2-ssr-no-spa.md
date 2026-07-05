---
status: accepted
---

# Server-rendered Jinja2 templates, no SPA

The frontend needs two flows: creating a paste (a form) and viewing one (rendering immutable text). A key requirement is that shared paste links unfurl correctly in Slack and iMessage, which scrape the raw HTML of a URL without executing JavaScript.

A pure React SPA was considered and rejected: it can't satisfy link unfurling (content only appears after client-side JS fetches it), and it adds round trips before the user sees their own pasted text. A Next.js SSR frontend was also considered and rejected — it solves unfurling, but requires running a second, separate Node.js runtime alongside the Python backend purely to render pages whose actual complexity (some text, a couple of Open Graph meta tags, an optional copy button) doesn't need React's component model or client hydration. Rendering each paste to a static file at write time and serving it from S3 was considered too, but was rejected in favor of render-per-request SSR: it couples paste storage to two systems (DynamoDB plus a rendered artifact store), and makes future edits harder, since updating content would mean regenerating and re-uploading a file rather than just changing a cache header.

Decision: both flows are served as plain server-rendered HTML via Jinja2 templating in the Python backend — one Python service, one runtime, no separate frontend build step or JS framework. This also keeps the future mutable-Paste path simple: an edit flow is just another server-rendered form-and-redirect, and switching a paste's cache behavior from "cache forever" (immutable) to "revalidate" (editable) is a header/config change rather than a rendering-technology change.
