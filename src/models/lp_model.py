from ortools.sat.python import cp_model
from models.entities import WashingMachine, Task
from typing import List

def solve_scheduling_problem(machines: List[WashingMachine], tasks: List[Task]):
    model = cp_model.CpModel()
    # Map machine types to available machines
    machines_by_type = {}
    for m in machines:
        machines_by_type.setdefault(m.type, []).append(m.id)
    # Decision variables: start time for each task
    start_vars = {}
    end_vars = {}
    late_vars = {}
    horizon = max(t.due_time for t in tasks) + max(t.length for t in tasks)
    for t in tasks:
        start = model.NewIntVar(t.arrival_time, horizon, f"start_{t.id}")
        end = model.NewIntVar(t.arrival_time, horizon, f"end_{t.id}")
        late = model.NewIntVar(0, horizon, f"late_{t.id}")
        model.Add(end == start + t.length)
        model.Add(late >= end - t.due_time)
        model.Add(late >= 0)
        start_vars[t.id] = start
        end_vars[t.id] = end
        late_vars[t.id] = late
    # Machine assignment and capacity constraints
    # For each machine, build intervals for tasks assigned to it
    intervals_by_machine = {m.id: [] for m in machines}
    assigned_vars = {}
    for t in tasks:
        assigned_vars[t.id] = []
        for m in machines:
            if m.type == t.required_type:
                assigned = model.NewBoolVar(f"assigned_{t.id}_{m.id}")
                interval = model.NewOptionalIntervalVar(
                    start_vars[t.id], t.length, end_vars[t.id], assigned, f"interval_{t.id}_{m.id}")
                intervals_by_machine[m.id].append(interval)
                assigned_vars[t.id].append(assigned)
        # Task must be assigned to required_count machines of the right type
        model.Add(sum(assigned_vars[t.id]) == t.required_count)
    # No overlapping tasks on the same machine
    for m in machines:
        model.AddNoOverlap(intervals_by_machine[m.id])
    # Objective: minimize total lateness
    model.Minimize(sum(late_vars[t.id] for t in tasks))
    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    result = {}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for t in tasks:
            result[t.id] = {
                "start": solver.Value(start_vars[t.id]),
                "end": solver.Value(end_vars[t.id]),
                "late": solver.Value(late_vars[t.id]),
            }
    else:
        result = "No feasible solution found."
    return result
