# copypaste

## Running locally

### No Docker (using the `uv`-managed virtualenv)

```bash
uv sync                                              # install deps
uv run flask --app copypaste.app:create_app run      # run dev server
```

### Via Docker Compose (app + `dynamodb-local`, closer to prod)

```bash
docker compose build
docker compose up -d       # app on http://localhost:8080
docker compose down        # stop
```

### Tests

```bash
uv run pytest tests/unit           # unit only, local
docker compose run --rm app pytest # unit + integration
```
