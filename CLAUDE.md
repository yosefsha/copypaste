# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

copypaste is a pastebin-style web service. Users paste text into a textbox, submit it, and receive
a short URL that can be used later (from any device) to retrieve the same text. Pastes must be
persistent (durable storage) and cached for fast repeated access.

## Status

Scaffolded. Stack: Python 3.13, Flask, `boto3`, `jinja2-fragments`, `Flask-WTF`, managed with `uv`.
See `docs/adr/` for the decisions behind these choices, and `TASKS.md` for the implementation plan.

## Stack

- **Language/runtime**: Python 3.13
- **Package manager**: `uv` (`pyproject.toml` + `uv.lock`)
- **Web framework**: Flask (`ADR-004`), server-rendered Jinja2 templates (`ADR-003`)
- **Datastore**: DynamoDB via `boto3`, local dev/test via `amazon/dynamodb-local` in Docker Compose (`ADR-002`)
- **App layout**: `src/copypaste/` (package), `tests/unit/`, `tests/integration/`

## Commands

Local (no Docker), using the `uv`-managed virtualenv:
- Install deps: `uv sync`
- Run unit tests: `uv run pytest tests/unit`
- Run a single test: `uv run pytest tests/unit/test_health.py::test_healthz_returns_ok`
- Run the dev server: `uv run flask --app copypaste.app:create_app run`

Via Docker Compose (app + `dynamodb-local` on a shared network):
- Build: `docker compose build`
- Start the stack: `docker compose up -d` (app on `http://localhost:8080`)
- Stop the stack: `docker compose down`
- Run unit tests in-container: `docker compose run --rm app pytest tests/unit`
- Run integration tests (against `dynamodb-local`): `docker compose run --rm app pytest tests/integration`

## Architecture notes

- `src/copypaste/app.py` — Flask app factory (`create_app`), route registration.
- `src/copypaste/config.py` — env-driven config, including `DYNAMODB_ENDPOINT_URL` (unset in prod, set to
  `http://dynamodb-local:8000` in Compose) so the same code targets DynamoDB Local or real DynamoDB (`ADR-002`).
- Paste creation, short-URL generation/lookup, and caching are not yet implemented — see `TASKS.md` phases 2-3.

## Development methodology

Check out a dedicated branch off `main` for each step in [TASKS.md](./TASKS.md) (e.g. `git checkout -b
step/<short-slug>`) before starting work on it. Don't mix multiple steps into one branch.

Implement each step using TDD, following red-green-refactor:
1. **Red** — write a failing test for the behavior first, and confirm it fails.
2. **Green** — write the minimum code to make it pass, and confirm it passes.
3. **Refactor** — clean up the implementation (and test, if needed) while keeping it green.

Push each step's branch and open a PR. Never merge to `main` without explicit human approval — not
even when tests pass and the change looks safe.

Do not write implementation code without a preceding failing test.

## Further reading

- [CONTEXT.md](./CONTEXT.md) — domain glossary
- [Features.md](./Features.md) — planned features explicitly out of scope for now
- [docs/adr/](./docs/adr/) — architecture decision records
- [TASKS.md](./TASKS.md) — step-by-step implementation plan
