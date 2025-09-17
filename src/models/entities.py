

import uuid
from dataclasses import dataclass
from enum import Enum
from ortools.sat.python.cp_model import IntVar
from pydantic import BaseModel
from typing import Dict, List, Optional


# Task due date and length categories
class DueDateCategory(str, Enum):
    H12 = "12h"
    H24 = "24h"
    WEEK = "1w"

class TaskLengthCategory(str, Enum):
    XS = "1"
    S = "2"
    M = "4"
    L = "8"
    XL = "12"
    XXL = "24"


@dataclass
class ModelVariables:
    start_vars: Dict[str, IntVar]
    end_vars: Dict[str, IntVar]
    late_vars: Dict[str, IntVar]
    assigned_vars: Dict[str, List[IntVar]]  # Use IntVar for bools
    machines: List['WashingMachine']
    tasks: List['Task']

# Context dataclass to hold all info for a run
@dataclass
class Context:
    machines: List['WashingMachine']
    tasks: List['Task']
    horizon: Optional[int] = None




class MachineType(str, Enum):
    WASHER = "washer"
    DRIER = "drier"
    IRON = "iron"

class WashingMachine(BaseModel):
    id: str
    type: MachineType

class Task(BaseModel):
    id: str
    arrival_time: int  # When the task comes in (hour offset from start)
    length: TaskLengthCategory  # Duration of the task (T-shirt size)
    due: DueDateCategory  # Due date category (12h, 24h, 1w)
    required_type: MachineType # Type of machine required
    required_count: int # Number of machines required
    due_time: int      # Due time for the task

    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = str(uuid.uuid4())[:8]
        # Auto-calculate due_time if not provided, based on due category
        if 'due_time' not in data or data['due_time'] is None:
            arrival_time = data.get('arrival_time', 0)
            due = data.get('due', None)
            if due == DueDateCategory.H12 or due == 'H12' or due == '12h':
                data['due_time'] = arrival_time + 12
            elif due == DueDateCategory.H24 or due == 'H24' or due == '24h':
                data['due_time'] = arrival_time + 24
            elif due == DueDateCategory.WEEK or due == 'WEEK' or due == '1w':
                data['due_time'] = arrival_time + 7 * 24
            else:
                data['due_time'] = arrival_time + 24  # Default to 24h if unknown
        super().__init__(**data)
