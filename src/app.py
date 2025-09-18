
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import streamlit as st
from src.models.entities import WashingMachine, Task, Context, MachineType, TaskLengthCategory, DueDateCategory
from src.models.lp_model import solve_scheduling_problem
import plotly.figure_factory as ff
from datetime import datetime, timedelta

st.set_page_config(page_title="Wash Scheduler", layout="wide")
st.title("Wash Scheduler")


# Sidebar: Add machines and scheduling horizon
st.sidebar.header("Machines")
machine_types = [e.value for e in MachineType]
if "machines" not in st.session_state:
    st.session_state["machines"] = []
if st.sidebar.button("Add Washer"):
    st.session_state["machines"].append(WashingMachine(id=f"M{len(st.session_state['machines'])+1}", type=MachineType.WASHER))
if st.sidebar.button("Add Drier"):
    st.session_state["machines"].append(WashingMachine(id=f"M{len(st.session_state['machines'])+1}", type=MachineType.DRIER))
if st.sidebar.button("Add Iron"):
    st.session_state["machines"].append(WashingMachine(id=f"M{len(st.session_state['machines'])+1}", type=MachineType.IRON))
st.sidebar.write("Current machines:")
for m in st.session_state["machines"]:
    st.sidebar.write(f"{m.id}: {m.type.value}")

# Sidebar: Scheduling horizon (number of days)
if "num_days" not in st.session_state:
    st.session_state["num_days"] = 1
st.sidebar.write("")
st.sidebar.header("Scheduling Horizon")
num_days = st.sidebar.number_input("Number of days to schedule", min_value=1, value=st.session_state["num_days"])
st.session_state["num_days"] = num_days

# Main: Add tasks
st.header("Tasks")
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []
with st.form("add_task_form"):
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        horizon_hours = int(st.session_state["num_days"]) * 24
        arrival_time = st.selectbox(
            "Arrival (h)",
            options=list(range(horizon_hours)),
            index=0,
            format_func=lambda h: (datetime(2025, 1, 1) + timedelta(hours=h)).strftime("%b %d %H:%M")
        )
    with col2:
        tshirt_sizes = [(cat.name, cat.value) for cat in TaskLengthCategory]
        length = st.selectbox(
            "Length (T-shirt size)",
            options=list(TaskLengthCategory),
            format_func=lambda c: f"{c.name} ({c.value}h)"
        )
    with col3:
        required_type = st.selectbox("Type", machine_types, index=0)
    with col4:
        required_count = st.number_input("# Machines", min_value=1, value=1)
    with col5:
        due_category = st.selectbox(
            "Due Date",
            options=list(DueDateCategory),
            format_func=lambda c: {DueDateCategory.H12: "12h", DueDateCategory.H24: "24h", DueDateCategory.WEEK: "1 week"}[c]
        )
    submitted = st.form_submit_button("Add Task")
    if submitted:
        # Map due category to due_time in hours
        if due_category == DueDateCategory.H12:
            due_time = arrival_time + 12
        elif due_category == DueDateCategory.H24:
            due_time = arrival_time + 24
        else:
            due_time = arrival_time + 7 * 24
        due_time = min(due_time, horizon_hours - 1)
        t = Task(
            id=f"T{len(st.session_state['tasks'])+1}",
            arrival_time=arrival_time,
            length=length,
            required_type=MachineType(required_type),
            required_count=required_count,
            due=due_category,
            due_time=due_time,
        )
        st.session_state["tasks"].append(t)

if st.button("Clear Tasks"):
    st.session_state["tasks"] = []

st.write("### Current Tasks")
for t in st.session_state["tasks"]:
    st.write(f"{t.id}: Arrive {t.arrival_time}h, Length {t.length.name} ({t.length.value}h), Type {t.required_type.value}, # {t.required_count}, Due {t.due.name} ({t.due_time}h)")

# Optimize and visualize
if st.button("Optimize & Visualize"):
    if not st.session_state["machines"] or not st.session_state["tasks"]:
        st.error("Please add at least one machine and one task.")
    else:
        # Set horizon for all tasks (end of scheduling window)
        horizon = int(st.session_state["num_days"]) * 24
        for t in st.session_state["tasks"]:
            t.due_time = min(t.due_time, horizon)
        context = Context(machines=st.session_state["machines"], tasks=st.session_state["tasks"])
        import time
        start_time = time.time()
        result = solve_scheduling_problem(context)
        solve_time = time.time() - start_time
        if isinstance(result, dict):
            base_time = datetime(2025, 1, 1, 0, 0, 0)
            gantt_tasks = []
            num_delayed = 0
            for task_id, info in result.items():
                start = base_time + timedelta(hours=info["start"])
                end = base_time + timedelta(hours=info["end"])
                if info["late"] > 0:
                    num_delayed += 1
                machine = info.get("machine", "N/A")
                gantt_tasks.append(dict(Task=machine, Start=start, Finish=end, Resource=task_id, Description=task_id))
            # Solution stats
            st.subheader("Solution Stats")
            st.write(f"**Solution value (total lateness):** {sum(info['late'] for info in result.values())}")
            st.write(f"**Solution time:** {solve_time:.2f} seconds")
            st.write(f"**Number of tasks scheduled:** {len(result)}")
            st.write(f"**Number of tasks delayed:** {num_delayed}")
            # Gantt chart
            fig = ff.create_gantt(
                gantt_tasks,
                index_col="Task",  # Each row is a machine
                show_colorbar=True,
                group_tasks=True,
                showgrid_x=True,
                showgrid_y=True,
                title="Schedule (Start: Jan 1st, 2025, Tasks as bars, Machines as rows)",
            )
            st.plotly_chart(fig, use_container_width=True)
            # Table of tasks
            import pandas as pd
            st.subheader("Task Schedule Table")
            table_data = []
            for t in st.session_state["tasks"]:
                sched = result.get(t.id, {})
                table_data.append({
                    "TaskID": t.id,
                    "Arrival": t.arrival_time,
                    "Length": f"{t.length.name} ({t.length.value}h)",
                    "Type": t.required_type.value,
                    "# Machines": t.required_count,
                    "Due": f"{t.due.name} ({t.due_time}h)",
                    "Scheduled Start": sched.get("start", "-"),
                    "Scheduled End": sched.get("end", "-"),
                    "Late": sched.get("late", "-"),
                })
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.error("No feasible solution found.")
