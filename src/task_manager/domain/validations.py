"""
Pure validation functions for domain rules.

This module contains composable, pure functions for validating domain rules.
Each validation function takes inputs and returns a Result with either the
validated value or an error.
"""
from datetime import datetime
from .models import Task, Subtask, Status
from .results import Result


# ============================================================
# Status Transition Validations
# ============================================================

# Define valid status transitions as per SCOPE.md
VALID_STATUS_TRANSITIONS: dict[Status, set[Status]] = {
    Status.TODO: {Status.IN_PROGRESS, Status.CANCELLED},
    Status.IN_PROGRESS: {Status.TODO, Status.DONE, Status.CANCELLED},
    Status.DONE: {Status.IN_PROGRESS},  # Reopen
    Status.CANCELLED: {Status.TODO},  # Reopen
    Status.OVERDUE: {Status.IN_PROGRESS, Status.CANCELLED},
}


def validate_status_transition(
    from_status: Status | None,
    to_status: Status
) -> Result[Status]:
    """
    Validate that a status transition is allowed.
    Common for both tasks and subtasks.
    """
    if from_status is None:
        return Result.Ok(to_status)
    
    valid_targets = VALID_STATUS_TRANSITIONS.get(from_status, set())
    
    if to_status not in valid_targets:
        return Result.Err(
            f"Invalid status transition from '{from_status.value}' to '{to_status.value}'. "
            f"Allowed transitions: {', '.join(s.value for s in valid_targets) if valid_targets else 'none'}"
        )
    
    return Result.Ok(to_status)


# ============================================================
# Deadline Validations
# ============================================================

def validate_deadline(deadline: datetime | None) -> Result[datetime | None]:
    """
    Validate that deadline is not in the past.
    For create operations.
    """
    if deadline is None:
        return Result.Ok(None)
    
    today = datetime.now().date()
    if deadline.date() < today:
        return Result.Err(
            f"Deadline cannot be in the past. Got {deadline.date()}, expected today or later."
        )
    
    return Result.Ok(deadline)


def validate_deadline_for_update(
    old_deadline: datetime | None,
    new_deadline: datetime | None
) -> Result[datetime | None]:
    """
    Validate that new deadline is not in the past.
    For update operations - just check the new value.
    """
    if new_deadline is None:
        return Result.Ok(old_deadline)
    
    today = datetime.now().date()
    if new_deadline.date() < today:
        return Result.Err(
            f"Deadline cannot be in the past. Got {new_deadline.date()}, expected today or later."
        )
    
    return Result.Ok(new_deadline)


def validate_deadline_for_subtask(
    parent_deadline: datetime | None,
    subtask_deadline: datetime | None
) -> Result[datetime | None]:
    """
    Validate that subtask deadline does not exceed parent task deadline.
    Task deadline validation should have already happened.
    """
    if parent_deadline is None:
        return Result.Ok(subtask_deadline)
    
    if subtask_deadline is None:
        return Result.Ok(subtask_deadline)
    
    if subtask_deadline > parent_deadline:
        return Result.Err(
            f"Subtask deadline ({subtask_deadline.date()}) cannot exceed parent task deadline ({parent_deadline.date()})."
        )
    
    return Result.Ok(subtask_deadline)

# ============================================================
# Task Completion Constraint Validations
# ============================================================

def validate_task_completion_with_subtasks(
    task_status: Status,
    subtasks: list[Subtask]
) -> Result[Status]:
    """
    Validate that a task cannot be marked as DONE if any subtask is still TODO.
    """
    if task_status != Status.DONE:
        return Result.Ok(task_status)
    
    todo_subtasks = [s for s in subtasks if s.status == Status.TODO]
    
    if todo_subtasks:
        todo_descriptions = [s.description for s in todo_subtasks[:3]]
        todo_list = ", ".join(f"'{d}'" for d in todo_descriptions)
        more = f" and {len(todo_subtasks) - 3} more" if len(todo_subtasks) > 3 else ""
        
        return Result.Err(
            f"Cannot mark task as DONE because {len(todo_subtasks)} subtask(s) still have TODO status: "
            f"{todo_list}{more}."
        )
    
    return Result.Ok(task_status)

