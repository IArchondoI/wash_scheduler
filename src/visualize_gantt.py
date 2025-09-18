

import plotly.figure_factory as ff
import plotly.offline as pyo
from typing import Dict, Any, Optional
import uuid
from datetime import datetime, timedelta

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
    # All times are relative to Jan 1st, 2025, in hours
    base_time = datetime(2025, 1, 1, 0, 0, 0)
    bars = []
    for task_id, info in schedule.items():
        start = base_time + timedelta(hours=info['start'])
        end = base_time + timedelta(hours=info['end'])
        machine = info.get('machine', 'N/A')
        bars.append(dict(Task=machine, Start=start, Finish=end, Resource=task_id, Description=task_id))
    fig = ff.create_gantt(
        bars,
        index_col='Task',  # Each row is a machine
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
        title="Dry Clean Schedule (Start: Jan 1st, 2025, Tasks as bars, Machines as rows)",
        show_hover_fill=True,
        bar_width=0.4,
    )
    # Add TaskID as annotation on each bar
    # Add TaskID as annotation on each bar (works for plotly.graph_objects, not figure_factory)
    # Instead, add hovertext and rely on built-in labels for now
    # (ff.create_gantt groups by resource, so fig['data'] is per resource, not per task)
    # Plotly's figure_factory does not support per-bar text labels directly
    pyo.plot(fig, filename=filename, auto_open=auto_open)

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src.data.example_data import get_example_data
    from src.models.lp_model import solve_scheduling_problem
    machines, tasks = get_example_data()
    schedule = solve_scheduling_problem(machines, tasks)
    if isinstance(schedule, dict):
        run_id = str(uuid.uuid4())[:8]
        visualize_gantt(schedule, run_id=run_id)
    else:
        print("No feasible solution found, nothing to visualize.")
