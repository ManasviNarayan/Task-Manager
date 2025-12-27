# Design

## API Layer

The API layer is implemented as a thin HTTP adapter using Flask. Its sole responsibility is to translate HTTP requests into calls to application logic and to translate results into HTTP responses.

Application creation is centralized in a create_app factory function. All blueprint registration occurs inside this function to avoid global side effects and to keep application composition explicit and testable.

API versioning is handled using version-scoped blueprints mounted under /api/v{n}. Each version represents a stable external contract. Versions do not delegate to each other at runtime; when behavior is identical, multiple versions bind to the same handler function.

Routes are registered explicitly using add_url_rule instead of decorators. This separates route exposure from handler implementation and allows handlers to be reused across API versions without coupling them to a specific blueprint.

Handlers act as thin controllers. They deal with HTTP-specific concerns (request parsing, response formatting) and invoke application or domain-level logic. Business rules and persistence are intentionally excluded from the API layer.

Flask-specific constructs are confined to the API layer. Domain and application logic remain framework-agnostic to allow future changes without impacting core behavior.

---
## 1. API Layer (`task_manager.api`)

**Responsibility:**  
- Exposes the system’s functionality via HTTP endpoints (Flask).  
- Handles request deserialization and response serialization.  
- Enforces boundary validation for inputs/outputs.  

**Key Design Decisions:**  
- **Blueprints & Versioning:** Endpoints are grouped using Flask Blueprints and versioned (`/api/v1/...`) for future backward compatibility.  
- **Handlers as Thin Controllers:** Each handler delegates to the service layer. The handler is responsible for input validation (via Pydantic schemas) and converting domain objects to JSON-serializable dicts.  
- **Schemas:** Pydantic schemas act as a contract boundary between domain and API, using enums with `use_enum_values=True` to serialize domain enums to JSON.  
- **Separation of Concerns:** API layer contains no business logic; it only adapts between HTTP and domain/service layers.

---

## 2. Service Layer (`task_manager.services`)

**Responsibility:**  
- Implements business logic and orchestrates operations across repositories and units of work.  
- Exposes domain-meaningful operations to the API layer.  

**Key Design Decisions:**  
- **Dependency Injection:** Services depend on abstracted Unit of Work (UoW) interfaces, enabling swapping in-memory or database implementations.  
- **UoW Integration:** All modifications to tasks/subtasks/history are done through UoW to ensure atomic operations.  
- **Domain Focused:** Services work entirely with domain objects; no HTTP, JSON, or persistence concerns leak here.

---

## 3. Unit of Work (`task_manager.data.unit_of_work`)

**Responsibility:**  
- Coordinates multiple repositories to maintain transactional integrity.  
- Exposes commit/rollback semantics.  

**Key Design Decisions:**  
- **Interface-based Design:** UoW depends on repository interfaces, allowing multiple implementations (in-memory vs database).  
- **Encapsulation:** Services interact with UoW; they don’t manage repositories directly.  
- **Implementation Variants:** Currently in-memory for learning, with a DB implementation planned for the future.

---

## 4. Repository Layer (`task_manager.data.repositories`)

**Responsibility:**  
- Abstracts data access for tasks, subtasks, and history.  
- Provides CRUD operations in a domain-centric manner.  

**Key Design Decisions:**  
- **Interface-driven:** Services depend on repository interfaces, not concrete implementations.  
- **Implementation Variants:** Separate in-memory and future database implementations.  
- **Domain Models:** Repositories return domain objects (`TaskModel`) rather than raw dicts.

---

## 5. Domain Layer (`task_manager.domain`)

**Responsibility:**  
- Contains core business entities, enums, and domain rules.  
- Defines authoritative types and constraints (e.g., `TaskModel`, `Status`, `Priority`).  

**Key Design Decisions:**  
- **Immutable/Plain Data Structures:** Domain models are simple `@dataclass` objects.  
- **Enums for Valid Values:** `Status` and `Priority` enums ensure consistent, centralized rules.  
- **No Infrastructure Dependency:** Domain objects are completely independent of persistence, HTTP, or schemas.

---

## 6. Infrastructure Layer (`task_manager.infrastructure`)

**Responsibility:**  
- Provides low-level implementations for storage or external systems.  

**Key Design Decisions:**  
- **In-memory DB for learning:** Uses Python lists/dicts to simulate persistence.  
- **Future-proofed:** Structured so that a relational database implementation can replace in-memory storage without impacting higher layers.  
- **Decoupled from Domain:** Infrastructure depends on repository interfaces, not domain logic.

---

### Design Principles Across Layers

- **Separation of Concerns:** Each layer has a single responsibility.  
- **Dependency Direction:** Higher layers depend on abstractions, not implementations.  
- **Boundary Enforcement:** API layer and schema validation isolate the outside world from domain logic.  
- **Testability:** In-memory implementations allow end-to-end testing without external dependencies.  
- **Future-proofing:** Versioned APIs, interface-based UoW, and repository abstractions enable easy replacement and extension.
