# Project Scope

## Overview

This project implements a **single-user To-Do Management backend service**.  
The system provides APIs for managing tasks and subtasks with enforced domain rules, persistence, and history tracking.

The scope is intentionally limited to focus on correctness, maintainability, and clear separation of concerns.

---

## In Scope

### Core Features

#### Task Management
- Create, update, retrieve, and filter tasks
- Tasks contain:
  - description
  - deadline
  - status
  - priority
  - subtasks

#### Subtask Management
- Create and update subtasks associated with a task
- Subtasks cannot exist independently of a task

#### Status Management
- Supported task and subtask statuses:
  - `TODO`
  - `IN_PROGRESS`
  - `DONE`
  - `CANCELLED`
  - `OVERDUE`
- Status transitions are validated and restricted
- Tasks automatically transition to `OVERDUE` when deadlines are exceeded
- Task status changes cascade to associated subtasks where applicable

#### Priority Management
- Supported priorities:
  - `LOW`
  - `MEDIUM`
  - `HIGH`
  - `CRITICAL`

#### History Tracking
- All task and subtask state changes are recorded
- History entries include:
  - timestamp
  - entity identifier
  - change type
  - previous and new values
- History persistence is atomic with the corresponding operation

---

## Persistence

- Relational database storage (SQLite for initial implementation)
- Data entities:
  - tasks
  - subtasks
  - history
- Database access is abstracted via repositories
- Domain models are decoupled from ORM models

---

## API

- REST-style HTTP API implemented using Flask
- Controllers are intentionally thin and limited to:
  - request deserialization
  - response serialization
  - error mapping
- Business logic is not implemented in the API layer

---

## Validation and Error Handling

- Input and domain validations are performed using composable validation functions
- Validation failures are handled consistently and surfaced via API responses
- Application errors are separated from infrastructure-level errors

---

## Transactions

- Write operations execute within explicit transaction boundaries
- Task, subtask, and history updates are committed atomically
- Transaction management is abstracted from application and domain logic

---

## Logging

- Centralized logging configuration
- Module-level loggers
- Configurable verbosity per subsystem

---

## Out of Scope

The following features are explicitly excluded:

- User authentication or authorization
- Multi-user support
- Frontend or UI
- Background jobs or schedulers
- Distributed systems or messaging
- CQRS, Event Sourcing, Saga patterns
- Caching layers
- Performance optimization
- Deployment, CI/CD, or infrastructure automation

---

## Constraints

- The system assumes a single user
- The service is not designed for horizontal scalability
- Framework and database choices must not leak into domain logic

---

## Non-Goals

- Production-scale performance
- Cloud-native deployment
- Feature parity with full task management systems

---

## Future Considerations

The following may be explored in later iterations:
- Background reminders
- Read-only query optimization
- Alternative persistence implementations
- Frontend or CLI integration
