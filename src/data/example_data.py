
from src.models.entities import WashingMachine, Task, MachineType

def get_example_data():
    machines = [
        WashingMachine(id="M1", type=MachineType.WASHER),
        WashingMachine(id="M2", type=MachineType.WASHER),
        WashingMachine(id="M3", type=MachineType.DRIER),
        WashingMachine(id="M4", type=MachineType.IRON),
    ]
    tasks = [
        Task(id="T1", arrival_time=0, length=3, required_type=MachineType.WASHER, required_count=1, due_time=5),
        Task(id="T2", arrival_time=1, length=2, required_type=MachineType.DRIER, required_count=1, due_time=6),
        Task(id="T3", arrival_time=2, length=4, required_type=MachineType.WASHER, required_count=2, due_time=10),
        Task(id="T4", arrival_time=3, length=1, required_type=MachineType.IRON, required_count=1, due_time=7),
    ]
    return machines, tasks
