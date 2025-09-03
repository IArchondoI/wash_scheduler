

import uuid
from enum import Enum
from pydantic import BaseModel


class MachineType(str, Enum):
    WASHER = "washer"
    DRIER = "drier"
    IRON = "iron"

class WashingMachine(BaseModel):
    id: str
    type: MachineType

class Task(BaseModel):
    id: str
    arrival_time: int  # When the task comes in
    length: int        # Duration of the task
    required_type: MachineType # Type of machine required
    required_count: int # Number of machines required
    due_time: int      # Due time for the task

    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = str(uuid.uuid4())[:8]
        super().__init__(**data)
