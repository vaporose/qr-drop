# QRDrop backend

FastAPI + WebSockets service for QRDrop. Session state (metadata, participants,
and message history) lives only in memory for the lifetime of a session — nothing
is written to disk.

## Run

```bash
uv sync
uv run fastapi run app/main.py        # production
uv run fastapi dev app/main.py        # auto-reload for development
```

The ASGI application is exposed as `app.main:app`, so any ASGI server works, e.g.:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> **Single process only.** Session state is in-memory, so the service must run as
> a single worker. Multiple workers/replicas would not share sessions.

## Configuration

Settings are loaded via Dynaconf from `config/settings.toml` (see `config.py`).
Select the environment with `ENV_FOR_DYNACONF` (`development` / `production`);
override any value with `APP_`-prefixed environment variables.

## Test

```bash
uv run pytest
```
