# task_manager/api/schemas.py
from task_manager.domain.models import Status, Priority, Task
from pydantic import BaseModel
from datetime import datetime
from dataclasses import asdict

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
        return cls(**asdict(task))
    
    def to_domain_model(self):
        return Task(
            id=self.id,
            description=self.description,
            deadline=self.deadline,
            status=Status(self.status),
            priority=Priority(self.priority)
        )
