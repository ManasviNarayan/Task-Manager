# Task Manager

A robust, single-user Task Management backend service built with Clean Architecture principles. Provides RESTful APIs for managing tasks and subtasks with enforced domain rules, persistence, and history tracking.

---

## Overview

This project implements a **single-user To-Do Management backend service** using Python and Flask. The system provides APIs for managing tasks and subtasks with enforced business rules, validation, persistence, and complete audit history.

### Key Features

- **Task Management**: Create, read, update, delete, and filter tasks
- **Subtask Hierarchy**: Break down complex tasks into manageable subtasks
- **Status Workflow**: Enforced valid status transitions
- **Priority Handling**: LOW, MEDIUM, HIGH, CRITICAL priority levels
- **Deadline Tracking**: Optional deadlines with automatic overdue detection
- **History Auditability**: Complete audit trail of all changes
- **Domain Validation**: Business rules enforced at the domain layer

---

## Architecture

The project follows **Clean Architecture** with clear layer separation:

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
│                    Domain Layer                             │
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
│   - Concrete implementations (in-memory database)         │
│   - Storage mechanics                                       │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| API | Flask |
| Validation | Pydantic |
| Domain | Python Enums, Dataclasses |
| Persistence | In-memory (current), SQLite (future) |
| Logging | Python standard `logging` |

---

## Project Structure

```
Task-Manager/
├── src/task_manager/
│   ├── __init__.py
│   ├── exceptions.py          # Custom exception classes
│   ├── logger.py               # Logger factory
│   ├── api/
│   │   ├── app.py             # Flask application setup
│   │   ├── providers.py        # Dependency injection
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── handlers/
│   │   │   ├── tasks.py       # Task request/response transformation
│   │   │   └── subtasks.py    # Subtask request/response transformation
│   │   └── v1/
│   │       ├── blueprints.py  # Versioned blueprint registration
│   │       └── routes/
│   │           ├── tasks.py   # Task URL routing
│   │           └── subtasks.py # Subtask URL routing
│   ├── services/
│   │   ├── tasks.py           # Task business logic
│   │   └── subtasks.py        # Subtask business logic
│   ├── domain/
│   │   ├── models.py          # Domain entities (Task, Subtask, Status, Priority, History, HistoryType)
│   │   ├── results.py         # Result monad for explicit error handling
│   │   ├── validations.py     # Domain validation functions
│   │   └── pipelines.py       # Validation pipeline factories
│   ├── data/
│   │   ├── repositories/
│   │   │   ├── interfaces.py  # Repository abstractions
│   │   │   └── in_memory.py   # In-memory implementations
│   │   └── unit_of_work/
│   │       ├── interfaces.py  # UoW abstractions
│   │       └── in_memory.py   # In-memory implementations
│   └── infrastructure/
│       ├── __init__.py
│       └── in_memory.py       # In-memory database
├── ARCHITECURE.md             # Detailed architecture documentation
├── DESIGN_DECISONS.md         # Architectural decisions and rationale
├── SCOPE.md                   # Project scope and requirements
├── pyproject.toml             # Project configuration
└── main.py                    # Application entry point
```

---

## API Endpoints

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tasks` | List all tasks |
| GET | `/api/v1/tasks/<task_id>` | Get a specific task |
| POST | `/api/v1/tasks` | Create a new task |
| PUT | `/api/v1/tasks/<task_id>` | Update a task |
| DELETE | `/api/v1/tasks/<task_id>` | Delete a task |
| GET | `/api/v1/tasks/history` | Get all history entries |
| GET | `/api/v1/tasks/history/<task_id>` | Get history for a specific task |

### Subtasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tasks/<task_id>/subtasks` | List all subtasks for a task |
| GET | `/api/v1/tasks/<task_id>/subtasks/<subtask_id>` | Get a specific subtask |
| POST | `/api/v1/tasks/<task_id>/subtasks` | Create a new subtask |
| PUT | `/api/v1/tasks/<task_id>/subtasks/<subtask_id>` | Update a subtask |
| DELETE | `/api/v1/tasks/<task_id>/subtasks/<subtask_id>` | Delete a subtask |
| GET | `/api/v1/tasks/<task_id>/subtasks/history` | Get subtask history for a task |
| GET | `/api/v1/tasks/<task_id>/subtasks/history/<subtask_id>` | Get history for a specific subtask |

---

## Task Attributes

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | string | No | auto-generated | Unique identifier |
| description | string | Yes | - | Task description |
| deadline | datetime | No | None | Due date |
| status | Status | No | TODO | Current status |
| priority | Priority | No | LOW | Priority level |

## Subtask Attributes

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | string | No | auto-generated | Unique identifier |
| task_id | string | Yes | - | Parent task ID |
| description | string | Yes | - | Subtask description |
| deadline | datetime | No | None | Due date |
| status | Status | No | TODO | Current status |

---

## Status Values

| Status | Description |
|--------|-------------|
| TODO | Task/Subtask is pending |
| IN_PROGRESS | Task/Subtask is actively being worked on |
| DONE | Task/Subtask has been completed |
| CANCELLED | Task/Subtask was cancelled |
| OVERDUE | Task/Subtask has passed its deadline |

## Valid Status Transitions

| From Status | Allowed To Status |
|-------------|-------------------|
| TODO | IN_PROGRESS, CANCELLED |
| IN_PROGRESS | TODO, DONE, CANCELLED |
| DONE | IN_PROGRESS (reopen) |
| CANCELLED | TODO (reopen) |
| OVERDUE | IN_PROGRESS, CANCELLED |

## Priority Values

| Priority | Value |
|----------|-------|
| LOW | 1 |
| MEDIUM | 2 |
| HIGH | 3 |
| CRITICAL | 4 |

---

## Domain Rules

### Input Validation
- Description must be non-empty (minimum 1 character)
- All enum fields must use valid values only
- Deadline must not be in the past

### Business Rules
- **Subtask Deadline Constraint**: A subtask's deadline cannot exceed its parent task's deadline
- **Task Completion Constraint**: A task cannot be marked as DONE if any of its subtasks are still in TODO status
- **Status Cascade**: When a task transitions to DONE or CANCELLED, all its subtasks receive the same status automatically

---

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

```bash
# Navigate to the project directory
cd Task-Manager

# Install dependencies
pip install -e .
```

### Running the Application

```bash
# Start the Flask development server
python main.py
```

The API will be available at `http://localhost:5000`

### Running Tests

```bash
# Run pytest
pytest
```

---

## Design Highlights

### Functional Programming Elements
- **Result Monad**: Explicit error handling with `Ok()` and `Err()` types
- **Validators**: Composable pure functions for domain rules
- **Pipelines**: Pre-configured validation chains

### Key Patterns Implemented
- Repository Pattern for data abstraction
- Unit of Work Pattern for transaction management
- Provider Pattern for dependency injection
- Context Manager for automatic resource cleanup

---

## Future Considerations

The architecture is designed to support:

- **Database Implementation**: Swap in-memory storage for SQLite
- **Background Jobs**: Overdue detection and reminders
- **API Evolution**: Versioned endpoints for backward compatibility

---

## Documentation

- [Architecture](ARCHITECURE.md) - Detailed technical architecture
- [Design Decisions](DESIGN_DECISONS.md) - Rationale behind architectural choices
- [Scope](SCOPE.md) - Project requirements and scope

---

## License

MIT License

