# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask-based REST API for whole-home automation (thermostat, garage door, lights, scenes, sump pump, devices). Deployed on a Raspberry Pi via systemd/uwsgi. Uses Auth0 (RS256 JWTs) for authentication, PostgreSQL for storage, RabbitMQ for device messaging, and mDNS (zeroconf) for local device discovery.

## Commands

### Run locally (non-Pi development)
```
python local_app.py
```
Production entry point (`app.py`) requires RPi.GPIO and cannot run on non-Pi machines.

### Run all tests (unit + integration)
```
./run_all_tests.sh
```
Requires Docker running. Starts a Postgres container, runs Flyway migrations, executes tests, and tears down.

### Run unit tests only
```
python3 -m pytest -s test/unit
```

### Run a single test file or test
```
python3 -m pytest -s test/unit/controllers/test_thermostat_controller.py
python3 -m pytest -s test/unit/controllers/test_thermostat_controller.py::TestThermostatTempController::test_get_user_temp__should_call_is_jwt_valid
```

### Run integration tests (requires Docker Postgres + Flyway running)
```
docker-compose up -d
# wait for postgres-home-automation to be healthy
python3 -m pytest -s test/integration
docker-compose down
```

### Install dependencies
```
pip install -Ur requirements.txt
pip install -Ur requirements_test.txt
```

## Architecture

**Request flow:** Routes → Controllers → Services/Repositories/Utilities

- `svc/endpoints/` — Flask blueprint route definitions, one file per domain. Routes are thin: extract request data, call a controller, return a `Response`.
- `svc/controllers/` — Business logic functions, one file per domain. Controllers orchestrate repositories, services, and utilities.
- `svc/services/` — External API integrations (e.g., weather).
- `svc/db/repositories/` — Database access via repository pattern. All repositories inherit from `DatabaseBase` and are used as context managers (`with UserRepository() as db:`).
- `svc/db/models/` — SQLAlchemy ORM models.
- `svc/models/` — `@dataclass_json`/`@dataclass` DTOs for API request/response shapes.
- `svc/utilities/` — Shared stateless helpers.
- `svc/constants/` — Domain constants organized via nested classes (e.g., `Automation.HVAC.QUEUE`).
- `svc/config/` — `Settings` singleton (accessed via `Settings.get_instance()`), security headers middleware.
- `svc/manager.py` — Flask app factory: registers all blueprints, initializes RabbitMQ queues, starts mDNS listener.

**Configuration:** `settings.<environment>.json` files at project root. Environment determined by `PYTHON_ENVIRONMENT` env var (defaults to `local`). Sensitive values support env var overrides via `_get_setting()` helper in `settings_state.py`.

**Database migrations:** Flyway, stored in `docker/flyway/migration/` with `V<version>__<description>.sql` naming.

## Code Style

- snake_case for variables/functions. No docstrings. No comments unless I ask.
- f-strings only for string formatting.
- Use `werkzeug.exceptions` (e.g., `Unauthorized`, `BadRequest`) for HTTP errors — never `flask.abort()`.
- Route return: `Response(data, status=<code>, mimetype=Mime.JSON)` using the `Mime` constants class.
- No nested/inner functions. No global variables. No imports inside functions.
- Private functions go at the bottom of the file, prefixed with `__`.
- Prefer functions over classes unless state management is necessary.

## Testing Style

- Framework: pytest. Mocking: `mock.patch` (from `mock` library, not `unittest.mock`).
- Arrange/act/assert format, no comments in tests.
- Test naming: `test_<function_name>__should_<expected_behavior>` (double underscore separator).
- Prefer bare test functions for simple cases. Use class-based tests (with `setup_method`) only when there is shared setup or shared class-level `@patch` decorators. No pytest fixtures.
- Class-level `@patch` decorators for mocks shared across tests; parameters injected in reverse decorator order.
- Class-level `UPPER_SNAKE_CASE` constants for immutable test data; instance attributes in `setup_method` for mutable data.
- Unit tests for routes: mock the entire controller module, use `test_request_context`.
- Unit tests for controllers: mock repositories, JWT validation, and external calls at the module path where imported.
- Integration tests: use Flask test client (`app.test_client()`), seed/clean up real DB in `setup_method`/`teardown_method`.
- Test directory mirrors `svc/` structure under `test/unit/`. Integration tests in `test/integration/`.
