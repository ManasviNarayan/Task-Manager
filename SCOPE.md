# Project Scope

## Overview

This project implements a **single-user To-Do Management backend service**.  
The system provides APIs for managing tasks and subtasks with enforced domain rules, persistence, and history tracking.

The scope is intentionally limited to focus on correctness, maintainability, and clear separation of concerns.

---

## Business Requirements

The Task Manager system must support the following business requirements:

1. **Single-User Task Management**: The system serves a single user and does not require authentication or multi-user support.

2. **Task Lifecycle Management**: Users must be able to create, read, update, delete, and filter tasks throughout their lifecycle.

3. **Subtask Hierarchy**: Tasks can contain multiple subtasks, allowing users to break down complex tasks into manageable units.

4. **Deadline Tracking**: Tasks support optional deadlines for time-sensitive items. The system must automatically detect and mark overdue tasks.

5. **Status Workflow**: The system enforces valid status transitions and supports reopening completed or cancelled tasks.

6. **Priority Handling**: Tasks support priority levels to help users focus on important items.

7. **History Auditability**: All task and subtask state changes must be recorded for audit purposes.

---

## Functional Requirements

### Task Management
- **Create Task**: Users can create a task with only a description (minimum required field)
- **Read Task**: Retrieve individual tasks or list all tasks
- **Update Task**: Modify task properties (description, deadline, status, priority)
- **Delete Task**: Remove a task and its associated subtasks

### Subtask Management
- **Create Subtask**: Add subtasks to an existing task
- **Read Subtask**: Retrieve subtasks for a specific task
- **Update Subtask**: Modify subtask properties
- **Delete Subtask**: Remove a subtask from a task
- **Cascade Status**: When a task transitions to DONE or CANCELLED, all its subtasks receive the same status

### Status Management
- Supported statuses: TODO, IN_PROGRESS, DONE, CANCELLED, OVERDUE
- Status transitions must follow defined rules
- Tasks automatically transition to OVERDUE when deadlines are exceeded

### Priority Management
- Supported priorities: LOW (1), MEDIUM (2), HIGH (3), CRITICAL (4)
- Default priority is LOW (value: 1) when not specified
- Integer values allow for easy filtering and natural ordering

### History Tracking
- All state changes are recorded with timestamp
- History entries include entity identifier, change type, previous and new values
- History persistence is atomic with the corresponding operation

---

## In Scope

### Core Features

#### Task Management
- Create, update, retrieve, and filter tasks
- Tasks contain:
  - description (required)
  - deadline (optional - can be blank for general tasks)
  - status (defaults to TODO)
  - priority (defaults to LOW)
  - subtasks

#### Task Creation
- Users can create a task with minimal information
- Only **description** is required to create a task
- Optional fields with defaults:
  - **deadline**: If not provided, the task is a general task with no specific due date
  - **status**: Defaults to `TODO` if not specified
  - **priority**: Defaults to `LOW` if not specified
- Task ID is auto-generated if not provided

#### Subtask Management
- Create and update subtasks associated with a task
- Subtasks cannot exist independently of a task
- Each subtask contains:
  - description (required)
  - deadline (optional - must not exceed parent task deadline)
  - status (defaults to TODO)
- **Note**: Subtasks do NOT have a priority field

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
  - `LOW` (value: 1)
  - `MEDIUM` (value: 2)
  - `HIGH` (value: 3)
  - `CRITICAL` (value: 4)
- Integer values allow for easy filtering and natural ordering (1 < 2 < 3 < 4)

#### History Tracking
- All task and subtask state changes are recorded
- History entries include:
  - id: Unique identifier for the history entry
  - entity_id: ID of the task or subtask that was changed
  - entity_type: Type of entity ("task" or "subtask")
  - change_type: What happened (created, updated, deleted)
  - timestamp: When the change occurred
  - old_value: Previous state (JSON serialized)
  - new_value: New state (JSON serialized)
- History can be queried for all entities or filtered by specific task/subtask
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
- Separate request and response schemas for create and fetch operations

---

## Domain-Level Validations

The following domain rules are enforced by the system:

### Input Validation
- Description must be non-empty (minimum length of 1 character)
- All enum fields (Status, Priority) must use valid values only
- **Deadline must not be in the past**: When creating or updating a task, the deadline (if provided) must be a future date or datetime

### Status Transition Rules
The following status transitions are valid:

| From Status | Allowed To Status |
|-------------|-------------------|
| TODO        | IN_PROGRESS, CANCELLED |
| IN_PROGRESS | TODO, DONE, CANCELLED |
| DONE        | IN_PROGRESS (reopen) |
| CANCELLED   | TODO (reopen) |
| OVERDUE     | IN_PROGRESS, CANCELLED |

### Business Rule Validations
- **Subtask Deadline Constraint**: A subtask's deadline cannot exceed its parent task's deadline
- **Task Completion Constraint**: A task cannot be marked as DONE if any of its subtasks are still in TODO status
- **ID Uniqueness**: Task IDs must be unique across the system

### Automatic Status Updates
- Tasks are automatically marked as OVERDUE when the current date exceeds the deadline

---

### Status Cascade to Subtasks
When a task transitions to DONE or CANCELLED, all its subtasks receive the same status automatically.

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
- Background overdue detection
- Background today task reminders
- Task filtering by various criteria
- Read-only query optimization
- Alternative persistence implementations
- Frontend or CLI integration

