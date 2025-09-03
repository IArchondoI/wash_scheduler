from models.entities import WashingMachine, Task

def get_example_data():
    machines = [
        WashingMachine(id="M1", type="standard"),
        WashingMachine(id="M2", type="standard"),
        WashingMachine(id="M3", type="delicate"),
    ]
    tasks = [
        Task(id="T1", arrival_time=0, length=3, required_type="standard", required_count=1, due_time=5),
        Task(id="T2", arrival_time=1, length=2, required_type="delicate", required_count=1, due_time=6),
        Task(id="T3", arrival_time=2, length=4, required_type="standard", required_count=2, due_time=10),
    ]
    return machines, tasks
