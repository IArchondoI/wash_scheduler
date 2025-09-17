from src.models.entities import WashingMachine, Task, Context, MachineType, TaskLengthCategory, DueDateCategory
from src.models.lp_model import solve_scheduling_problem

def generate_tasks(n):
    tasks = []
    for i in range(n):
        arrival_time = 0
        length = TaskLengthCategory.S  # 2 hours
        due = DueDateCategory.H24
        # Calculate due_time based on due category
        if due == DueDateCategory.H12:
            due_time = arrival_time + 12
        elif due == DueDateCategory.H24:
            due_time = arrival_time + 24
        else:
            due_time = arrival_time + 7 * 24
        tasks.append(Task(
            id=f"T{i}",
            arrival_time=arrival_time,
            length=length,
            required_type=MachineType.WASHER,
            required_count=1,
            due=due,
            due_time=due_time,
        ))
    return tasks

def test_large_batch():
    machines = [WashingMachine(id=f"M{j}", type=MachineType.WASHER) for j in range(25)]
    tasks = generate_tasks(50)
    context = Context(machines=machines, tasks=tasks)
    result = solve_scheduling_problem(context)
    assert isinstance(result, dict), f"Expected dict, got {type(result)}: {result}"
    assert len(result) == 50, f"Expected 50 tasks in result, got {len(result)}"
    for task_id, info in result.items():
        assert info["end"] - info["start"] == int(TaskLengthCategory.S.value), f"Task {task_id} does not have length 2"
