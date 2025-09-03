
import plotly.figure_factory as ff
import plotly.offline as pyo
from typing import Dict, Any, Optional
import uuid

def visualize_gantt(
    schedule: Dict[str, dict[str, Any]],
    filename: Optional[str] = None,
    auto_open: bool = True,
    run_id: Optional[str] = None,
) -> None:
    """
    Visualize the schedule as a Gantt chart and save as HTML (optionally open in browser).
    schedule: Dict mapping task ids to dicts with 'start', 'end', and optionally 'machine' keys.
    filename: Optional custom filename. If not provided, uses run_id or generates a new one.
    run_id: Optional run identifier to use in the filename.
    """
    if filename is None:
        if run_id is None:
            run_id = str(uuid.uuid4())[:8]
        filename = f"gantt_{run_id}.html"
    tasks = []
    for task_id, info in schedule.items():
        start = info['start']
        end = info['end']
        machine = info.get('machine', 'N/A')
        tasks.append(dict(Task=task_id, Start=start, Finish=end, Resource=machine))
    fig = ff.create_gantt(
        tasks,
        index_col='Resource',
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
    )
    pyo.plot(fig, filename=filename, auto_open=auto_open)

if __name__ == "__main__":
    from src.data.example_data import get_example_data
    from src.models.lp_model import solve_scheduling_problem
    machines, tasks = get_example_data()
    schedule = solve_scheduling_problem(machines, tasks)
    if isinstance(schedule, dict):
        run_id = str(uuid.uuid4())[:8]
        visualize_gantt(schedule, run_id=run_id)
    else:
        print("No feasible solution found, nothing to visualize.")
