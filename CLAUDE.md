# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

copypaste is a pastebin-style web service. Users paste text into a textbox, submit it, and receive
a short URL that can be used later (from any device) to retrieve the same text. Pastes must be
persistent (durable storage) and cached for fast repeated access.

## Status

This repository is unstarted — no tech stack, dependencies, or code have been chosen yet. Do not
assume a language, framework, or database. Confirm these with the user before scaffolding anything.

Once the stack is chosen and the project is scaffolded, update this file with:
- Build / lint / test / run commands (including how to run a single test)
- Architecture notes: how paste creation, short-URL generation/lookup, persistence, and caching fit together

## Development methodology

Implement each step in [TASKS.md](./TASKS.md) using TDD: write a failing test for the behavior first,
then write the minimum code to make it pass, then refactor. Do not write implementation code without
a preceding failing test.

## Further reading

- [CONTEXT.md](./CONTEXT.md) — domain glossary
- [Features.md](./Features.md) — planned features explicitly out of scope for now
- [docs/adr/](./docs/adr/) — architecture decision records
- [TASKS.md](./TASKS.md) — step-by-step implementation plan
