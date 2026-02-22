from task_manager.domain.models import Status, Priority
from pydantic import BaseModel
from datetime import datetime

class TaskPayload(BaseModel):
    id : str | None
    description : str
    deadline: datetime
    status: Status
    priority : Priority

    model_config = {
        "use_enum_values": True
    }