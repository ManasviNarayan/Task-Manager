# Design

## API Layer

The API layer is implemented as a thin HTTP adapter using Flask. Its sole responsibility is to translate HTTP requests into calls to application logic and to translate results into HTTP responses.

Application creation is centralized in a create_app factory function. All blueprint registration occurs inside this function to avoid global side effects and to keep application composition explicit and testable.

API versioning is handled using version-scoped blueprints mounted under /api/v{n}. Each version represents a stable external contract. Versions do not delegate to each other at runtime; when behavior is identical, multiple versions bind to the same handler function.

Routes are registered explicitly using add_url_rule instead of decorators. This separates route exposure from handler implementation and allows handlers to be reused across API versions without coupling them to a specific blueprint.

Handlers act as thin controllers. They deal with HTTP-specific concerns (request parsing, response formatting) and invoke application or domain-level logic. Business rules and persistence are intentionally excluded from the API layer.

Flask-specific constructs are confined to the API layer. Domain and application logic remain framework-agnostic to allow future changes without impacting core behavior.