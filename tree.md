```src/task_manager/
├── __init__.py
├── exceptions.py          # Custom exception classes
├── logger.py              # Logger factory
├── api/
│   ├── __init__.py
│   ├── app.py             # Flask application setup
│   ├── providers.py        # Dependency injection
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── tasks.py       # Task request/response transformation
│   │   └── subtasks.py    # Subtask request/response transformation
│   └── v1/
│       ├── __init__.py
│       ├── blueprints.py  # Versioned blueprint registration
│       └── routes/
│           ├── __init__.py
│           ├── tasks.py   # Task URL routing
│           └── subtasks.py # Subtask URL routing
├── services/
│   ├── __init__.py
│   ├── tasks.py           # Task business logic
│   └── subtasks.py        # Subtask business logic
├── domain/
│   ├── __init__.py
│   ├── models.py          # Domain entities (Task, Subtask, Status, Priority, History, HistoryType)
│   ├── results.py         # Result monad for explicit error handling
│   ├── validations.py     # Domain validation functions
│   └── pipelines.py      # Validation pipeline factories
├── data/
│   ├── __init__.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── interfaces.py  # Repository abstractions (ITaskRepository, ISubtaskRepository, IHistoryRepository)
│   │   └── in_memory.py   # In-memory implementations
│   └── unit_of_work/
│       ├── __init__.py
│       ├── interfaces.py  # UoW abstractions (ITaskUnitOfWork, ISubtaskUnitOfWork)
│       └── in_memory.py   # In-memory implementations
└── infrastructure/
    ├── __init__.py
    └── in_memory.py       # In-memory database
```