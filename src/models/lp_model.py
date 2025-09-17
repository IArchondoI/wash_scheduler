
from ortools.sat.python import cp_model
from src.models.entities import Context, ModelVariables
from typing import Dict, Any, Tuple, Union

def create_scheduling_model(
    context: Context
) -> Tuple[cp_model.CpModel, ModelVariables]:
    """
    Create the CP-SAT model for the dry clean scheduling problem.
    Returns the model and a ModelVariables dataclass for later extraction.
    """
    model = cp_model.CpModel()
    machines = context.machines
    tasks = context.tasks
    machines_by_type = {}
    for m in machines:
        machines_by_type.setdefault(m.type, []).append(m.id)
    start_vars = {}
    end_vars = {}
    late_vars = {}
    assigned_vars = {}
    intervals_by_machine = {m.id: [] for m in machines}
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
        assigned_vars[t.id] = []
        for m in machines:
            if m.type == t.required_type:
                assigned = model.NewBoolVar(f"assigned_{t.id}_{m.id}")
                interval = model.NewOptionalIntervalVar(
                    start, t.length, end, assigned, f"interval_{t.id}_{m.id}"
                )
                intervals_by_machine[m.id].append(interval)
                assigned_vars[t.id].append(assigned)
        model.Add(sum(assigned_vars[t.id]) == t.required_count)
    for m in machines:
        model.AddNoOverlap(intervals_by_machine[m.id])
    model.Minimize(sum(late_vars[t.id] for t in tasks))
    variables = ModelVariables(
        start_vars=start_vars,
        end_vars=end_vars,
        late_vars=late_vars,
        assigned_vars=assigned_vars,
        machines=machines,
        tasks=tasks,
    )
    return model, variables

def solve_model(model: cp_model.CpModel) -> Tuple[cp_model.CpSolver, Any]:
    """
    Solve the given CP-SAT model and return the solver and status.
    """
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    return solver, status

def extract_solution(
    solver: cp_model.CpSolver, status: Any, variables: ModelVariables
) -> Union[Dict[str, Any], str]:
    """
    Extract the solution from the solver and variables if feasible.
    Returns a dictionary mapping task IDs to their schedule.
    """
    tasks = variables.tasks
    start_vars = variables.start_vars
    end_vars = variables.end_vars
    late_vars = variables.late_vars
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

def solve_scheduling_problem(context: Context) -> Union[Dict[str, Any], str]:
    """
    High-level function to create, solve, and extract the solution for the scheduling problem.
    """
    model, variables = create_scheduling_model(context)
    solver, status = solve_model(model)
    return extract_solution(solver, status, variables)
