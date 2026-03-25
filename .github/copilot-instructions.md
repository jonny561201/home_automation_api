# These Are GitHub Copilot Instructions for Python

Be clear and concise. No need for extra encouragement.
Avoid public code that will be excluded by license copyright.
Don't always agree with me. Challenge my assumptions.
Ask me clarifying questions. Don't guess when you don't have enough information.
Stay on task with what I asked for, don't anticipate what I might do next.
Remind me to commit often before moving to the next task.
Do things one step at a time, confirming with me before moving on.
Don't add comments unless I tell you to do so.


### Code Styles
- Use 4 spaces per indentation level.
- Prefer using functions over classes unless state management is necessary.
- Functions should follow SOLID principles, especially single responsibility.
- Use snake_case for variable and function names.
- Use f-strings for all string formatting — never use %-formatting or str.format().
- route or endpoint methods should be as lightweight as possible, delegating logic to service or utility functions.
- use flask blueprints to organize routes by functionality.
- do not use docstrings unless this is a library for public consumption.
- Private methods should be at the bottom of a class or code file.
- NEVER nest functions inside other functions (ie: inner functions).
- NEVER use global variables.
- NEVER import modules inside functions or methods.
- Use werkzeug.exceptions (e.g., Unauthorized, BadRequest, FailedDependency) for HTTP error responses — never use flask.abort().
- Use the repository pattern with Python context managers (with ... as database:) for all database access. Repositories should inherit from DatabaseBase.
- Access settings through the Settings singleton via Settings.get_instance() — never read config files or environment variables directly in business logic.
- Route functions should return Response(data, status=<code>, mimetype=Mime.JSON) — use the Mime constants class, not raw strings.

### Testing Styles
- Use mock.patch from the mock library, not unittest.mock.
- Tests should be written using pytest framework.
- Tests should be written in an arrange/act/assert format without comments.
- Prefer bare test functions when tests are simple and self-contained. Only use class-based test organization (with `setup_method`/`teardown_method`) when there is significant shared setup overhead or shared class-level `@patch` decorators. Do not use pytest fixtures.
- Test method naming convention: test_<function_name>__should_<expected_behavior> (double underscore separator).
- Use class-level @patch decorators for mocks shared across all or most tests in a class; patch parameters are injected in reverse decorator order.
- Class-level constants (UPPER_SNAKE_CASE) for immutable test data; instance-level attributes set in setup_method for mutable test data.
- Unit tests for routes should mock the entire controller module and use a Flask test_request_context.
- Unit tests for controllers should mock repositories, JWT validation, and external service calls at the module path where they are imported.
- Integration tests should use the Flask test client (app.test_client()), seed/clean up real database records in setup_method/teardown_method.


### File and Folder Conventions
- Favor using MVC architecture for organizing code.
- The `app.py` file is used to start the app in production and `local_app.py` is used for local development.


 ### Architecture Conventions
- Routes → Controllers → Services/Repositories/Utilities: routes delegate to controllers, controllers orchestrate business logic using repositories, services, and utility functions.
- svc/endpoints/ contains Flask blueprint route definitions — one file per domain (e.g., thermostat_routes.py).
- svc/controllers/ contains business logic functions — one file per domain (e.g., thermostat_controller.py).
- svc/models/ contains @dataclass_json/@dataclass DTOs for API request/response shapes.
- svc/db/models/ contains SQLAlchemy ORM model definitions.
- svc/db/repositories/ contains database access classes using the repository pattern.
- svc/services/ contains functions for external API integrations.
- svc/utilities/ contains shared stateless helper functions.
- svc/constants/ contains constant values organized by domain using nested classes.
- svc/config/ contains app configuration and middleware (e.g., Settings singleton, security headers).
- test/unit/ mirrors the svc/ folder structure. test/integration/ contains end-to-end route tests.


### Configuration Conventions
- Settings files are named settings.<environment>.json at the project root. The environment is determined by the PYTHON_ENVIRONMENT env var (defaults to local).
- Sensitive settings support environment variable overrides — the _get_setting helper checks the env var first, then falls back to the JSON file.
- Database migrations use Flyway and are stored in docker/flyway/migration/ with versioned naming (V<version>__<description>.sql).