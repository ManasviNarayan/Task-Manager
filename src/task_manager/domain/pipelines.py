"""
Validation pipelines - composable validation chains.

Pipelines define which validations to run in which order.
Validators tell what to check, pipelines tell when to use them.
"""
from typing import Callable, List
from .results import Result, combine
from . import validations


# ============================================================
# Pipeline Factory
# ============================================================

def create_pipeline(validators: List[Callable[[], Result]]) -> Result:
    """
    Create a validation pipeline from a list of validator callables.
    
    Each validator is a callable that returns a Result.
    All validators are run and errors are accumulated.
    """
    results = [v() for v in validators]
    return combine(*results)


# ============================================================
# Task Create Pipeline
# ============================================================

def task_create_validation_pipeline(deadline) -> Result:
    """Pipeline for validating task creation."""
    return create_pipeline([
        lambda: validations.validate_deadline(deadline)
    ])


# ============================================================
# Subtask Create Pipeline
# ============================================================

def subtask_create_validation_pipeline(parent_deadline, subtask_deadline) -> Result:
    """Pipeline for validating subtask creation."""
    return create_pipeline([
        lambda: validations.validate_deadline_for_subtask(parent_deadline, subtask_deadline)
    ])


# ============================================================
# Task Update Pipeline
# ============================================================

def task_update_validation_pipeline(old_task, new_deadline, new_status) -> Result:
    """Pipeline for validating task updates."""
    validators: List[Callable[[], Result]] = [
        lambda: validations.validate_deadline_for_update(old_task.deadline, new_deadline)
    ]
    
    if new_status is not None:
        validators.append(lambda: validations.validate_status_transition(old_task.status, new_status))
    
    return create_pipeline(validators)


# ============================================================
# Subtask Update Pipeline
# ============================================================

def subtask_update_validation_pipeline(parent_task, old_subtask, new_deadline, new_status) -> Result:
    """Pipeline for validating subtask updates."""
    effective_deadline = new_deadline if new_deadline is not None else old_subtask.deadline
    
    validators: List[Callable[[], Result]] = [
        lambda: validations.validate_deadline_for_subtask(parent_task.deadline, effective_deadline)
    ]
    
    if new_status is not None:
        validators.append(lambda: validations.validate_status_transition(old_subtask.status, new_status))
    
    return create_pipeline(validators)


# ============================================================
# Task Status Change Pipeline
# ============================================================

def task_status_change_pipeline(task, new_status, subtasks) -> Result:
    """Pipeline for validating task status changes."""
    return create_pipeline([
        lambda: validations.validate_status_transition(task.status, new_status),
        lambda: validations.validate_task_completion_with_subtasks(new_status, subtasks)
    ])


# ============================================================
# Delete Pipelines (may be empty for now)
# ============================================================

def task_delete_validation_pipeline(task) -> Result:
    """Pipeline for validating task deletion."""
    # Currently no validations needed for delete
    return Result.Ok(None)


def subtask_delete_validation_pipeline(subtask) -> Result:
    """Pipeline for validating subtask deletion."""
    # Currently no validations needed for delete
    return Result.Ok(None)

