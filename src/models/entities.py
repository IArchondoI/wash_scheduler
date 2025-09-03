from pydantic import BaseModel

class WashingMachine(BaseModel):
    id: str
    type: str

class Task(BaseModel):
    id: str
    arrival_time: int  # When the task comes in
    length: int        # Duration of the task
    required_type: str # Type of machine required
    required_count: int # Number of machines required
    due_time: int      # Due time for the task
