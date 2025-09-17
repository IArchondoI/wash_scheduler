
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import streamlit as st
from src.models.entities import WashingMachine, Task, Context, MachineType
from src.models.lp_model import solve_scheduling_problem
import plotly.figure_factory as ff
from datetime import datetime, timedelta

st.set_page_config(page_title="Wash Scheduler", layout="wide")
st.title("Wash Scheduler")

# Sidebar: Add machines
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

# Main: Add tasks
st.header("Tasks")
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []
with st.form("add_task_form"):
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        arrival_time = st.number_input("Arrival (h)", min_value=0, value=0)
    with col2:
        length = st.number_input("Length (h)", min_value=1, value=2)
    with col3:
        required_type = st.selectbox("Type", machine_types, index=0)
    with col4:
        required_count = st.number_input("# Machines", min_value=1, value=1)
    with col5:
        due_time = st.number_input("Due (h)", min_value=1, value=4)
    submitted = st.form_submit_button("Add Task")
    if submitted:
        t = Task(
            id=f"T{len(st.session_state['tasks'])+1}",
            arrival_time=arrival_time,
            length=length,
            required_type=MachineType(required_type),
            required_count=required_count,
            due_time=due_time,
        )
        st.session_state["tasks"].append(t)

if st.button("Clear Tasks"):
    st.session_state["tasks"] = []

st.write("### Current Tasks")
for t in st.session_state["tasks"]:
    st.write(f"{t.id}: Arrive {t.arrival_time}h, Length {t.length}h, Type {t.required_type.value}, # {t.required_count}, Due {t.due_time}h")

# Optimize and visualize
if st.button("Optimize & Visualize"):
    if not st.session_state["machines"] or not st.session_state["tasks"]:
        st.error("Please add at least one machine and one task.")
    else:
        context = Context(machines=st.session_state["machines"], tasks=st.session_state["tasks"])
        result = solve_scheduling_problem(context)
        if isinstance(result, dict):
            base_time = datetime(2025, 1, 1, 0, 0, 0)
            gantt_tasks = []
            for task_id, info in result.items():
                start = base_time + timedelta(hours=info["start"])
                end = base_time + timedelta(hours=info["end"])
                gantt_tasks.append(dict(Task=task_id, Start=start, Finish=end, Resource="N/A"))
            fig = ff.create_gantt(
                gantt_tasks,
                index_col="Resource",
                show_colorbar=True,
                group_tasks=True,
                showgrid_x=True,
                showgrid_y=True,
                title="Schedule (Start: Jan 1st, 2025, Task lengths in hours)",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No feasible solution found.")
