
import uuid
from dataclasses import dataclass
from enum import Enum
from ortools.sat.python.cp_model import IntVar
from pydantic import BaseModel
from typing import Dict, List

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
