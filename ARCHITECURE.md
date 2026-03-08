# Architecture

## Overview

This document describes the architecture of the Task Manager backend service. It builds upon the [Scope](../SCOPE.md) document and provides technical details on how the system is structured and how data flows through it.

---

## Technology Stack

The system uses the following technologies:

| Layer | Technology | Purpose |
|-------|------------|---------|
| API | Flask | HTTP request handling and routing |
| Validation | Pydantic | Request/response schema validation |
| Domain | Python Enums, Dataclasses | Business entities and rules |
| Persistence | In-memory (current), SQLite (future) | Data storage |
| Logging | Python standard `logging` | Structured logging |

**Rationale**: Flask provides a lightweight HTTP layer. Pydantic offers built-in validation with clear error messages. Python's enum and dataclass modules provide native domain modeling without additional dependencies. See [Design Decisions](./DESIGN_DECISONS.md) for detailed rationale.

---

## Layer Architecture

The system follows **Clean Architecture** with clear layer separation. Each layer has specific responsibilities and dependencies flow inward toward the domain.

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (Flask)                        │
│   - HTTP handling, request/response transformation          │
│   - Pydantic schema validation                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
│   - Business logic orchestration                           │
│   - Transaction coordination                               │
│   - Domain rule enforcement                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                              │
│   - Core business entities (Task, Status, Priority)        │
│   - Domain rules and validations                           │
│   - Pure, no external dependencies                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│   - Repository interfaces (abstractions)                  │
│   - Unit of Work (transaction boundaries)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                        │
│   - Concrete implementations (in-memory database)          │
│   - Storage mechanics                                       │
└─────────────────────────────────────────────────────────────┘
```

### 1. API Layer (`task_manager.api`)

**Responsibility:**  
- Exposes the system's functionality via HTTP endpoints (Flask).  
- Handles request deserialization and response serialization.  
- Enforces boundary validation for inputs/outputs.  

**Key Design Decisions:**  
- **Blueprints & Versioning:** Endpoints are grouped using Flask Blueprints and versioned (`/api/v1/...`) for future backward compatibility.
- **Separation between Handler and Blueprints:** Handlers for request/response have been kept separate from blueprints to allow different versions to point to same handlers to avoid code duplication.
- **Handlers as Thin Controllers:** Each handler delegates to the service layer. The handler is responsible for input validation (via Pydantic schemas) and converting domain objects to JSON-serializable dicts.  
- **Schemas:** Pydantic schemas act as a contract boundary between domain and API, using enums with `use_enum_values=True` to serialize domain enums to JSON.
- **Schema Conversion Methods:** Schemas implement `from_domain_model()` class method and `to_domain_model()` instance method for bidirectional conversion between domain models and API payloads.
- **Providers:** Centralizes construction and wiring of service-layer dependencies and acts as a dependency injector for handlers and API endpoints. Factory functions return Unit of Work instances.
- **Context Manager Integration:** Handlers use the `with` statement with Unit of Work for automatic transaction management (commit on success, rollback on exception).
- **Separation of Concerns:** API layer contains no business logic; it only adapts between HTTP and domain/service layers.

---

### 2. Service Layer (`task_manager.services`)

**Responsibility:**  
- Implements business logic and orchestrates operations across repositories and units of work.  
- Exposes domain-meaningful operations to the API layer.  

**Key Design Decisions:**  
- **Dependency Injection:** Services depend on abstracted Unit of Work (UoW) interfaces, enabling swapping in-memory or database implementations.  
- **UoW Integration:** All modifications to tasks/subtasks/history are done through UoW to ensure atomic operations.  
- **Domain Focused:** Services work entirely with domain objects; no HTTP, JSON, or persistence concerns leak here.

---

### 3. Unit of Work (`task_manager.data.unit_of_work`)

**Responsibility:**  
- Coordinates multiple repositories to maintain transactional integrity.  
- Exposes commit/rollback semantics.  

**Key Design Decisions:**  
- **Interface-based Design:** UoW depends on repository interfaces, allowing multiple implementations (in-memory vs database).  
- **Context Manager Protocol:** UoW implements `__enter__` and `__exit__` methods to enable Python's `with` statement for automatic transaction management.
- **Automatic Commit/Rollback:** On successful completion, `__exit__` calls `commit()`. On exception, `__exit__` calls `rollback()` to ensure data consistency.
- **Encapsulation:** Services interact with UoW; they don't manage repositories directly.  
- **Implementation Variants:** Currently in-memory for learning, with a DB implementation planned for the future.

---

### 4. Repository Layer (`task_manager.data.repositories`)

**Responsibility:**  
- Abstracts data access for tasks, subtasks, and history.  
- Provides CRUD operations in a domain-centric manner.  

**Key Design Decisions:**  
- **Interface-driven:** Services depend on repository interfaces, not concrete implementations.  
- **Implementation Variants:** Separate in-memory and future database implementations.  
- **Domain Models:** Repositories return domain objects (`Task`) rather than raw dicts.

---

### 5. Domain Layer (`task_manager.domain`)

**Responsibility:**  
- Contains core business entities, enums, and domain rules.  
- Defines authoritative types and constraints (e.g., `Task`, `Status`, `Priority`).  

**Key Design Decisions:**  
- **Immutable/Plain Data Structures:** Domain models are simple `@dataclass` objects.  
- **Enums for Valid Values:** `Status` and `Priority` enums ensure consistent, centralized rules.  
- **No Infrastructure Dependency:** Domain objects are completely independent of persistence, HTTP, or schemas.

---

### 6. Infrastructure Layer (`task_manager.infrastructure`)

**Responsibility:**  
- Provides low-level implementations for storage or external systems.  

**Key Design Decisions:**  
- **In-memory DB for learning:** Uses Python lists/dicts to simulate persistence.  
- **Future-proofed:** Structured so that a relational database implementation can replace in-memory storage without impacting higher layers.  
- **Decoupled from Domain:** Infrastructure depends on repository interfaces, not domain logic.

---

## Data Flow

Understanding how requests flow through the system helps explain why the architecture is structured this way.

### Request Flow: Create Task

```
1. HTTP Request arrives
         │
         ▼
2. Flask routes to handler (api/v1/routes/tasks.py)
         │
         ▼
3. Handler receives request, calls Pydantic schema to validate (api/schemas.py)
         │
         ▼ [if valid]
4. Handler calls provider to get Unit of Work
         │
         ▼
5. Handler enters context manager (with uow:)
         │
         ▼
6. Handler creates Service, calls business method (services/tasks.py)
         │
         ▼
7. Service validates business rules, coordinates with Repository via UoW
         │
         ▼
8. Repository performs data operation (data/repositories/in_memory.py)
         │
         ▼
9. On success: __exit__ calls commit()
   On failure: __exit__ calls rollback()
         │
         ▼
10. Handler converts domain object to response schema
         │
         ▼
11. HTTP Response returned to client
```

### Transaction Flow

The Unit of Work ensures atomicity. All changes within a single request are committed together:

```python
# Handler code demonstrating transaction flow
def create_task(request):
    with get_task_uow() as uow:  # __enter__ - start transaction
        service = TaskService(uow)
        task = service.create_task(task_data)
        # ... more operations
    # __exit__ - commit if no exception, rollback if exception
    return TaskPayload.from_domain_model(task), 201
```

---

## Exception Handling

Exceptions are categorized by their source and handled appropriately at layer boundaries.

### Exception Hierarchy

```
Exception (built-in)
    │
    ├── ValidationError      # Business rule violations
    ├── NotFoundError        # Entity not found
    ├── DomainError          # General domain violations
    └── DatabaseError       # Infrastructure failures
```

### Error Flow Through Layers

```
Repository detects error
    │
    ▼
Service catches, logs, wraps if needed, re-raises
    │
    ▼
Flask error handler maps to HTTP response
    │
    ▼
Client receives JSON error response
```

### HTTP Status Mapping

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| Pydantic ValidationError | 400 | Invalid request structure |
| ValidationError | 400 | Business rule violation |
| NotFoundError | 404 | Resource not found |
| DomainError | 409 | Business logic conflict |
| DatabaseError | 500 | Infrastructure failure |

**Rationale**: This separation allows clients to distinguish between "they sent bad data" (400) and "they asked for something that doesn't exist" (404). See [Design Decisions - Error Handling](./DESIGN_DECISONS.md#3-error-handling-approach) for detailed rationale.

---

## Logging Architecture

Logging provides observability into system operations across all layers.

### Log Levels by Layer

| Layer | Level | What to Log |
|-------|-------|-------------|
| API Handlers | INFO | Request received, response sent |
| Services | INFO | Business operations, key decisions |
| Repositories | DEBUG | Query details, data access |
| Domain | WARNING | Unexpected states only |

### Implementation

```python
# Centralized logger factory
from task_manager.logger import get_logger

logger = get_logger(__name__, logging.INFO)
```

**Rationale**: Module-level loggers with configurable levels allow tuning verbosity without code changes. INFO at higher layers captures business intent; DEBUG at lower layers provides detail when needed. See [Design Decisions - Logging](./DESIGN_DECISONS.md#4-logging-strategy) for detailed rationale.

---

## Module Structure

```
src/task_manager/
├── __init__.py
├── exceptions.py          # Custom exception classes
├── logger.py              # Logger factory
├── api/
│   ├── __init__.py
│   ├── app.py             # Flask application setup
│   ├── providers.py        # Dependency injection
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── handlers/
│   │   └── tasks.py       # Request/response transformation
│   └── v1/
│       ├── __init__.py
│       ├── blueprints.py  # Versioned blueprint registration
│       └── routes/
│           └── tasks.py   # URL routing
├── services/
│   ├── __init__.py
│   └── tasks.py           # Business logic
├── domain/
│   ├── __init__.py
│   └── models.py          # Domain entities (Task, Status, Priority, History, HistoryType)
├── data/
│   ├── __init__.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── interfaces.py  # Repository abstractions (ITaskRepository, IHistoryRepository)
│   │   └── in_memory.py   # In-memory implementation
│   └── unit_of_work/
│       ├── __init__.py
│       ├── interfaces.py  # UoW abstraction (includes history property)
│       └── in_memory.py   # In-memory implementation
└── infrastructure/
    ├── __init__.py
    └── in_memory.py       # In-memory database
```

### History Feature
The history tracking feature is integrated throughout all layers:

- **Domain Layer**: `History` model and `HistoryType` enum track all entity changes
- **Data Layer**: `IHistoryRepository` interface with `get_history()` and `add_history()` methods
- **Service Layer**: `TaskService._record_history()` helper records changes atomically with each operation
- **API Layer**: `GET /tasks/history` and `GET /tasks/history/<task_id>` endpoints

---

## Design Principles

- **Separation of Concerns:** Each layer has a single responsibility.  
- **Dependency Direction:** Higher layers depend on abstractions, not implementations.  
- **Boundary Enforcement:** API layer and schema validation isolate the outside world from domain logic.  
- **Testability:** In-memory implementations allow end-to-end testing without external dependencies.  
- **Future-proofing:** Versioned APIs, interface-based UoW, and repository abstractions enable easy replacement and extension.

---

## Future Considerations

The architecture supports future enhancements without major refactoring:

### Database Implementation
- Repository and UoW interfaces are already defined
- In-memory implementation can be replaced with SQLite/ORM implementation
- Domain models are persistence-agnostic

### Background Jobs
- The service layer is structured to support background task integration
- Domain rules (overdue detection, reminders) can be implemented as scheduled jobs
- See [Scope - Background Processing](../SCOPE.md#background-processing)

### API Evolution
- Versioned routes (`/api/v1/`) allow backward-compatible changes
- Handler separation enables reusing business logic across API versions
- Schema versioning can be added as needed

### Additional Features
- Authentication middleware can be added at the API layer
- Caching can be introduced as a repository decorator
- Event publishing can be added for external integrations

