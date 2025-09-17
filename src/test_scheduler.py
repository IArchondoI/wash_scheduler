from src.models.entities import WashingMachine, Task, Context, MachineType
from src.models.lp_model import solve_scheduling_problem

def generate_tasks(n):
    return [
        Task(
            id=f"T{i}",
            arrival_time=0,
            length=2,
            required_type=MachineType.WASHER,
            required_count=1,
            due_time=4,
        )
        for i in range(n)
    ]

def test_large_batch():
    machines = [WashingMachine(id=f"M{j}", type=MachineType.WASHER) for j in range(25)]
    tasks = generate_tasks(50)
    context = Context(machines=machines, tasks=tasks)
    result = solve_scheduling_problem(context)
    assert isinstance(result, dict), f"Expected dict, got {type(result)}: {result}"
    assert len(result) == 50, f"Expected 50 tasks in result, got {len(result)}"
    for task_id, info in result.items():
        assert info["end"] - info["start"] == 2, f"Task {task_id} does not have length 2"
