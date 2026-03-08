# Design Decisions

This document captures key architectural and design decisions made during the development of this task management backend service. Each decision includes the context, alternatives considered, and rationale.

---

## Table of Contents
1. [Layer Separation & Clean Architecture](#1-layer-separation--clean-architecture)
2. [API Versioning Strategy](#2-api-versioning-strategy)
3. [Error Handling Approach](#3-error-handling-approach)
4. [Logging Strategy](#4-logging-strategy)
5. [Data Models & Naming](#5-data-models--naming)
6. [Repository Pattern](#6-repository-pattern)
7. [Unit of Work Pattern](#7-unit-of-work-pattern)
8. [In-Memory First Implementation](#8-in-memory-first-implementation)
9. [Single vs Multiple Payloads](#9-single-vs-multiple-payloads)
10. [Validation Strategy](#10-validation-strategy)
11. [What Was Explicitly Excluded](#11-what-was-explicitly-excluded)
12. [Provider Pattern & Dependency Injection](#12-provider-pattern--dependency-injection)
13. [Schema Bidirectional Conversion](#13-schema-bidirectional-conversion)
14. [Context Manager for Unit of Work](#14-context-manager-for-unit-of-work)

---

## 1. Layer Separation & Clean Architecture

### Decision
Implement Clean Architecture with the following layer structure:

```
api/            # HTTP concerns (Flask, request/response)
services/       # Business orchestration, transaction boundaries
domain/         # Business entities, rules, validation
data/           # Repositories and Unit of Work abstractions
infrastructure/ # Concrete implementations (in-memory DB)
```

### Alternatives Considered
- **Traditional MVC**: Everything in controllers/models - too coupled to framework
- **Simple layered architecture**: No strict dependency rules - domain logic can leak
- **Two layers only** (routes + models): Insufficient separation of concerns

### Rationale
- **Domain independence**: Business logic is isolated from frameworks and can be tested independently
- **Dependency direction**: Domain sits at the center with all dependencies pointing inward
- **Clear responsibilities**: Each layer has a single, well-defined purpose
- **Testability**: Each layer can be tested in isolation without external dependencies
- **Framework flexibility**: Could swap Flask for FastAPI without touching domain or service layers
- **Implementation flexibility**: Can swap storage implementations (in-memory → database) without changing domain logic

### Trade-offs
- ✅ Highly maintainable and extensible
- ✅ Clear separation of concerns
- ✅ Demonstrates understanding of architectural principles
- ⚠️ More initial setup compared to simple MVC
- ⚠️ May appear over-engineered for small scope (aimed towards learning)

---

## 2. API Versioning Strategy

### Decision
Separate routes from handlers to enable API versioning without code duplication.

```python
api/
├── handlers/tasks.py        # Request/response transformation logic
└── v1/routes/tasks.py       # URL routing and endpoint definitions for v1
```

### Alternatives Considered
- **Combined routes and handlers**: Simpler structure with single file per resource
- **Versioned handlers**: Duplicate handler code across API versions
- **No versioning structure**: Add versioning later when needed

### Rationale
- **Handler reuse**: If v2 changes only some endpoints, unchanged endpoints can reuse v1 handlers
- **Clear version boundaries**: Directory structure (`v1/routes/`) makes API versioning explicit
- **Future-proofing**: Enables API evolution without code duplication
- **Separation of concerns**: URL structure is separate from business logic

### Example
```python
# v1/routes/tasks.py
bp.add_url_rule('/tasks', view_func=get_tasks, methods=['GET'])

# v2/routes/tasks.py - can reuse the same handler
bp.add_url_rule('/tasks', view_func=get_tasks, methods=['GET'])

# Or use different handler if v2 requires changes
bp.add_url_rule('/tasks', view_func=get_tasks_v2, methods=['GET'])
```

### Trade-offs
- ✅ Supports API versioning without code duplication
- ✅ Clear intent and structure
- ⚠️ More files for a small project

---

## 3. Error Handling Approach

### Decision
Use Pydantic for structural validation at the API boundary and custom exceptions for business/domain errors.

### Error Hierarchy
```python
# Structural validation (API boundary)
Pydantic ValidationError → HTTP 400

# Business/domain errors
ValidationError    → HTTP 400 (business rule violation)
NotFoundError      → HTTP 404 (entity not found)
DomainError        → HTTP 409 (business logic conflict)
DatabaseError      → HTTP 500 (infrastructure failure)
```

### Alternatives Considered
- **Result/Either types**: Functional approach with explicit error paths
- **Generic exceptions only**: Loses type information and semantic meaning
- **HTTP status codes only**: No structured error information
- **Mix of all approaches**: Inconsistent error handling

### Rationale
- **Clear boundaries**: Pydantic validates structure (types, formats), custom exceptions handle business logic
- **Python-idiomatic**: Exceptions are natural in Python
- **Type safety**: Specific exception types enable precise error handling
- **Clean propagation**: Errors bubble up through layers and are caught at appropriate boundaries
- **Centralized handling**: Flask error handlers provide consistent JSON responses

### Error Flow
```
Repository throws DatabaseError
    ↓
Service catches, logs, and re-raises or wraps in DomainError
    ↓
Flask error handler converts to JSON response with proper HTTP status
```

### Trade-offs
- ✅ Clear separation between structural and business validation
- ✅ Follows Python conventions
- ✅ Type-safe error handling
- ✅ Can add Result types later if needed
- ⚠️ Error paths are not as explicit as functional Result types

---

## 4. Logging Strategy

### Decision
Use a centralized logger factory with module-level loggers configured at different levels per layer.

### Implementation
```python
# logger.py - single configuration point
def get_logger(name, level, fmt, datefmt) -> logging.Logger:
    # Configurable, reusable, prevents duplicate handlers
    ...

# Usage in each module
logger = get_logger(__name__, logging.INFO)
```

### Log Levels by Layer
- **API handlers**: INFO - track requests and responses
- **Services**: INFO - track business operations
- **Repositories**: DEBUG/ERROR - only log errors to avoid noise
- **Domain**: WARNING - domain should be silent unless critical

### Alternatives Considered
- **Print statements**: Not production-ready
- **Third-party logging** (structlog, loguru): Additional dependency
- **Per-module config files**: Over-complicated for this scope
- **Root logger only**: Loses granularity

### Rationale
- **Consistency**: All modules use the same format
- **Configurability**: Can adjust log levels per module without code changes
- **Prevents duplicates**: Checks for existing handlers before adding new ones
- **Production-ready**: Structured logs with configurable output
- **Clear context**: Using `__name__` provides module information in each log

### Trade-offs
- ✅ Single configuration point
- ✅ Production-ready approach
- ✅ Tunable verbosity per subsystem
- ⚠️ Less feature-rich than specialized logging libraries

---

## 5. Data Models & Naming

### Decision
Use `Task` for domain models and `TaskPayload` for API contracts.

```python
# Domain model
@dataclass
class Task:
    id: str | None
    description: str
    deadline: datetime
    status: Status
    priority: Priority

# API contract
class TaskPayload(BaseModel):
    id: str | None
    description: str
    deadline: datetime
    status: Status
    priority: Priority
    
    model_config = {"use_enum_values": True}
```

### Alternatives Considered
- **TaskModel / TaskSchema**: Ambiguous naming, "model" is overloaded
- **TaskEntity / TaskDTO**: Verbose and overly enterprise-focused
- **Single model for both**: Violates layer boundaries
- **Task / TaskResponse**: Less clear for bidirectional data flow

### Rationale
- **Clear intent**: `Task` represents the domain entity, `TaskPayload` represents wire format
- **Avoids naming conflicts**: Won't collide with future `TaskORM` when adding database
- **Explicit boundaries**: Shows that API layer owns the serialization contract
- **Enables independent evolution**: Domain and API can change independently

### When They Might Diverge
- Domain adds methods: `task.is_overdue()`, `task.can_close()`
- Domain has internal fields: `created_by`, `updated_at`
- API flattens nested structures or adds computed fields
- Different validation rules for domain vs API

### Trade-offs
- ✅ Clear semantic meaning
- ✅ Future-proof for database implementation
- ✅ Explicit layer boundaries
- ⚠️ Maintains two similar structures

---

## 6. Repository Pattern

### Decision
Define abstract repository interfaces with concrete in-memory implementations.

```python
# Interface
class ITaskRepository(ABC):
    @abstractmethod
    def get_tasks(self) -> List[Task]:
        pass

# Implementation
class InMemoryTaskRepository(ITaskRepository):
    def get_tasks(self) -> List[Task]:
        return [Task(**task) for task in self._db.tasks]
```

### Alternatives Considered
- **Direct database access**: Couples services to infrastructure
- **Active Record pattern**: Domain models know about persistence
- **No abstraction**: Simpler but inflexible

### Rationale
- **Decoupling**: Services depend on abstractions, not concrete storage
- **Testability**: Can inject fake repositories for testing
- **Flexibility**: Can swap storage implementations without changing services
- **Domain purity**: Repository handles persistence concerns, domain stays pure
- **Responsibility clarity**: Repository owns data transformation from storage to domain objects

### Key Decision: Repository Returns Domain Objects
```python
def get_tasks(self) -> List[Task]:
    raw_data = self._db.tasks  # Dicts from storage
    return [Task(**task) for task in raw_data]  # Transform to domain objects
```

**Why**: Service layer should only work with domain objects. The transformation from storage format to domain objects is the repository's responsibility.

### Trade-offs
- ✅ Clean abstraction
- ✅ Easy to swap implementations
- ✅ Domain isolation maintained
- ⚠️ More code than direct access

---

## 7. Unit of Work Pattern

### Decision
Use Unit of Work to manage transaction boundaries and coordinate multiple repositories.

```python
class ITaskUnitOfWork(ABC):
    @property
    def tasks(self) -> ITaskRepository:
        pass
    
    def commit(self): pass
    def rollback(self): pass
```

### Alternatives Considered
- **No UoW**: Services manage repositories directly
- **Repository-level transactions**: Violates single responsibility
- **Service-level transaction management**: Couples services to transaction mechanics

### Rationale
- **Atomic operations**: Ensures related changes (tasks + subtasks + history) are committed together
- **Encapsulation**: Services don't need to know about transaction details
- **Consistency**: Single commit point for all repository changes
- **Future-ready**: When adding database, UoW naturally wraps database sessions/transactions

### In-Memory Implementation
```python
def commit(self):
    logger.debug("Committing transaction (in-memory no-op)")

def rollback(self):
    logger.debug("Rolling back transaction (in-memory no-op)")
```

**Why no-op**: In-memory changes are immediate. Logging maintains the interface contract. Real implementation comes with database integration.

### Trade-offs
- ✅ Explicit transaction boundaries
- ✅ Prepared for database implementation
- ✅ Enables atomic multi-repository operations
- ⚠️ May seem over-engineered for in-memory storage

---

## 8. In-Memory First Implementation

### Decision
Build in-memory implementations first, then add database later.

### Development Approach
1. Define interfaces (`ITaskRepository`, `ITaskUnitOfWork`)
2. Implement in-memory versions
3. Build and test all features with in-memory storage
4. Swap to database implementation later (planned)

### Alternatives Considered
- **Database first**: More realistic but slower iteration
- **Mock/fake only**: Not executable, can't demo
- **SQLite from start**: Adds ORM complexity early

### Rationale
- **Fast iteration**: No database setup, migrations, or ORM complexity during development
- **Architecture focus**: Validates layer separation without infrastructure noise
- **Instant testability**: No test database setup needed
- **Proves abstraction**: Successfully swapping to database later validates the abstraction design

### Seed Data
```python
class InMemoryDB:
    def __init__(self):
        self.tasks = [
            {"id": "task-001", "description": "...", ...},
            {"id": "task-002", "description": "...", ...},
        ]
```

**Why seed data**: Enables manual testing and demonstrations without creating data first.

### Trade-offs
- ✅ Rapid development and testing
- ✅ No infrastructure dependencies
- ✅ Validates architecture works
- ⚠️ Not production-ready (acknowledged in project scope)
- ⚠️ Requires database implementation later

---

## 9. Single vs Multiple Payloads

### Decision
Use a single `TaskPayload` for both create and fetch operations.

```python
class TaskPayload(BaseModel):
    id: str | None  # None for create requests, str for fetch responses
    description: str
    deadline: datetime
    status: Status
    priority: Priority
```

### Alternatives Considered
- **Separate payloads**: `TaskCreatePayload` (no ID) and `TaskResponsePayload` (with ID)
- **Inheritance**: `TaskBase` with `TaskCreate` and `TaskResponse` subclasses
- **Different schemas per endpoint**: Maximum flexibility

### Rationale
- **Minimal difference**: Only the ID field differs between create and fetch
- **YAGNI**: Can split later if payloads diverge significantly
- **Reduced duplication**: Avoids maintaining nearly identical classes
- **Simplicity**: Easier to understand and maintain

### When to Split
Consider splitting if:
- Create requires fields not in response (e.g., passwords)
- Response has computed/derived fields (e.g., `is_overdue`)
- Validation rules differ significantly
- Nested objects appear in one but not the other

### Trade-offs
- ✅ Less code and duplication
- ✅ Simpler to maintain
- ✅ Easy to refactor when needed
- ⚠️ ID field semantics are implicit

---

## 10. Validation Strategy

### Decision
Implement multi-layer validation with different concerns per layer.

### Validation Layers
```python
# Layer 1: Pydantic (API boundary)
class TaskPayload(BaseModel):
    description: str  # Type validation, required field checks

# Layer 2: Domain validation (business rules)
def validate_status_transition(from_status, to_status):
    # Business logic validation
    if (from_status, to_status) in INVALID_TRANSITIONS:
        raise ValidationError("Cannot transition from X to Y")

# Layer 3: Service orchestration
def update_status(task_id, new_status):
    # Combines domain validation with data access
    validate_status_transition(task.status, new_status)
    # ... apply change
```

### Alternatives Considered
- **All validation in API**: Mixes structural and business concerns
- **All validation in domain**: Domain becomes aware of HTTP concepts
- **Database constraints only**: Catches errors too late
- **Third-party validators**: Additional dependencies

### Rationale
- **Pydantic at boundary**: Handles structural validation (types, formats, required fields)
- **Domain validation**: Enforces business rules (status transitions, deadlines, constraints)
- **Service orchestration**: Combines validation with transaction management
- **Clear separation**: Each layer validates what it owns

### Validation Examples by Layer
- **Pydantic**: "Is `deadline` a valid datetime format?"
- **Domain**: "Is the deadline in the future?"
- **Domain**: "Can a task transition from DONE to TODO?" (No)
- **Service**: "Can a critical task close if subtasks are open?" (No - cross-entity rule)

### Trade-offs
- ✅ Clear separation of validation concerns
- ✅ Each layer validates its responsibilities
- ✅ Composable validation logic
- ⚠️ Multiple validation points to maintain

---

## 11. What Was Explicitly Excluded

### Features Not Included and Why

#### Authentication & Authorization
- **Reason**: Orthogonal to domain modeling and architectural patterns
- **Can add later**: Yes, as middleware without touching domain layer

#### Multi-User Support
- **Reason**: Adds distributed system concerns (sessions, user context)
- **Can add later**: Yes, by adding `user_id` to domain models

#### Frontend / UI
- **Reason**: Project focuses on backend architecture
- **Can add later**: Yes, API is designed for frontend consumption

#### Background Jobs / Schedulers
- **Reason**: Infrastructure complexity (Celery, Redis) not relevant to core learning goals
- **Can add later**: Yes, as separate service layer concern

#### Caching
- **Reason**: Premature optimization, not demonstrating core architecture
- **Can add later**: Yes, as repository decorator or service layer addition

#### Deployment / CI/CD
- **Reason**: Focus is on code architecture, not DevOps
- **Can add later**: Yes, separate concern from application code

#### Advanced Patterns (CQRS, Event Sourcing, Saga)
- **Reason**: Over-engineering for domain complexity
- **Can add later**: Not appropriate for this domain

### Project Scope Philosophy
From the scope document:
> "The scope is intentionally limited to focus on correctness, maintainability, and clear separation of concerns."

These exclusions enable deeper focus on fundamental architectural patterns without the noise of infrastructure concerns.

---

## 12. Provider Pattern & Dependency Injection

### Decision
Use a centralized provider module to handle dependency creation and wiring, with factory functions that return Unit of Work instances.

### Implementation
```python
# api/providers.py
from task_manager.infrastructure.in_memory import InMemoryDB
from task_manager.data.unit_of_work.in_memory import InMemoryTaskUnitOfWork
from task_manager.data.unit_of_work.interfaces import ITaskUnitOfWork

_db = InMemoryDB()  # shared in-memory "session"

def get_task_list_uow() -> ITaskUnitOfWork:
    """Factory function to create Unit of Work instances.
    
    This allows for proper dependency injection while maintaining
    the factory pattern for creating new instances per request.
    """
    return InMemoryTaskUnitOfWork(_db)
```

### Usage in Handlers
```python
# api/handlers/tasks.py
def get_tasks() -> tuple[list[dict], int]:
    with get_task_list_uow() as uow:
        service = TaskService(uow)
        tasks = [TaskPayload.from_domain_model(task).model_dump() 
                 for task in service.get_tasks()]
        logger.info(f"Retrieved {len(tasks)} tasks")
    return tasks, HTTPStatus.OK
```

### Alternatives Considered
- **Direct instantiation in handlers**: Couples handlers to concrete implementations
- **Global service instances**: Not thread-safe, prevents proper isolation
- **Dependency injection frameworks** (e.g., punq, injector): Additional dependencies
- **Service locator pattern**: Implicit dependencies, harder to test

### Rationale
- **Explicit dependencies**: Factory functions make dependencies visible
- **Testability**: Can swap providers for mock implementations
- **Single responsibility**: Providers handle dependency creation, handlers handle HTTP
- **Flexibility**: Easy to change storage implementation (in-memory → database)
- **Context manager integration**: Works seamlessly with Unit of Work context managers

### Trade-offs
- ✅ Clear dependency flow
- ✅ Easy to test with mocks
- ✅ No external dependencies
- ⚠️ Manual provider management (vs. DI framework)

---

## 13. Schema Bidirectional Conversion

### Decision
Implement bidirectional conversion methods in Pydantic schemas to transform between domain models and API payloads.

### Implementation
```python
# api/schemas.py
class TaskPayload(BaseModel):
    id : str | None
    description : str
    deadline: datetime
    status: Status
    priority : Priority

    model_config = {
        "use_enum_values": True
    }

    @classmethod
    def from_domain_model(cls, task: Task):
        """Convert domain model to API payload."""
        return cls(**asdict(task))
    
    def to_domain_model(self):
        """Convert API payload to domain model."""
        return Task(
            id=self.id,
            description=self.description,
            deadline=self.deadline,
            status=Status(self.status),
            priority=Priority(self.priority)
        )
```

### Usage
```python
# Handler converting domain → API
task = service.get_task(task_id)
return TaskPayload.from_domain_model(task).model_dump(), HTTPStatus.OK

# Handler converting API → domain (for create/update)
payload = TaskPayload.model_validate(request.json)
task = payload.to_domain_model()
```

### Alternatives Considered
- **Separate response schemas**: Different classes for request/response
- **Automatic Pydantic serialization**: Less control over conversion
- **Manual dict mapping**: Error-prone, verbose
- **ORM-like mappers**: Additional complexity

### Rationale
- **Explicit conversion**: Clear where transformations happen
- **Type safety**: Leverages Pydantic validation
- **Single source of truth**: Schema defines both validation and conversion
- **Enum handling**: Properly reconstructs enum types from JSON values
- **Symmetric**: Both directions are supported

### Trade-offs
- ✅ Clear transformation logic
- ✅ Validated at each boundary
- ✅ Enum reconstruction is explicit
- ⚠️ Slight code duplication of field names

---

## 14. Context Manager for Unit of Work

### Decision
Implement `__enter__` and `__exit__` methods on Unit of Work to enable Python's `with` statement for automatic transaction management.

### Implementation
```python
# data/unit_of_work/interfaces.py
class ITaskUnitOfWork(ABC):
    @property
    @abstractmethod
    def tasks(self) -> ITaskRepository:
        pass

    @abstractmethod
    def __enter__(self) -> Self:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass
```

```python
# data/unit_of_work/in_memory.py
class InMemoryTaskUnitOfWork(ITaskUnitOfWork):
    def __init__(self, db):
        self._db = db
        self._tasks = InMemoryTaskRepository(db)

    @property
    def tasks(self) -> InMemoryTaskRepository:
        return self._tasks

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
            logger.error("Transaction rolled back due to exception: %s", exc_val)
        else:
            self.commit()
        return None
```

### Handler Usage
```python
def get_tasks() -> tuple[list[dict], int]:
    with get_task_list_uow() as uow:  # __enter__ called here
        service = TaskService(uow)
        tasks = service.get_tasks()
        # ... process tasks
    # __exit__ called here - commits on success, rolls back on exception
    return tasks, HTTPStatus.OK
```

### Alternatives Considered
- **Manual commit/rollback**: Error-prone, easy to forget
- **Decorator pattern**: More complex, less Pythonic
- **Service-level transaction**: Couples services to transaction logic
- **No transaction management**: Not suitable for database implementations

### Rationale
- **Pythonic**: Uses native context manager protocol
- **Automatic cleanup**: Ensures commit/rollback even on exceptions
- **Resource safety**: Prevents resource leaks
- **Future-proof**: Works naturally with database transactions
- **Clean handler code**: Separates transaction lifecycle from business logic

### Error Handling Flow
```
1. Handler enters 'with' block → __enter__ returns UoW
2. Service executes business logic
3. If no exception:
   - __exit__ is called with (None, None, None)
   - commit() is executed
4. If exception occurs:
   - __exit__ is called with exception info
   - rollback() is executed
   - Exception propagates to Flask error handler
```

### Trade-offs
- ✅ Automatic transaction management
- ✅ Pythonic and readable
- ✅ Ensures cleanup in all cases
- ⚠️ In-memory implementation is no-op (as expected)
- ⚠️ Requires understanding of context manager protocol

---

## Design Evolution

### Key Iterations

**Iteration 1: Architecture Validation**
- Built `GET /tasks` end-to-end
- Validated all layers connect properly
- Confirmed architecture feels natural with no awkward boundaries

**Iteration 2: Error Handling Infrastructure**
- Added exception hierarchy
- Implemented Flask error handlers
- Added logging throughout all layers

**Iteration 3: Code Quality Refinement**
- Changed `__dict__` to `asdict()` for proper dataclass serialization
- Renamed `TaskModel` → `Task`, `TaskSchema` → `TaskPayload` for clarity
- Modified repository to return domain objects instead of dicts

**Iteration 4: Dependency Injection & Context Management**
- Added provider pattern for dependency creation (`api/providers.py`)
- Implemented context manager protocol (`__enter__`/`__exit__`) on Unit of Work
- Added bidirectional schema conversion methods (`from_domain_model`/`to_domain_model`)
- Integrated context managers in handlers for automatic transaction management
