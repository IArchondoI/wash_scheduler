from models.lp_model import solve_scheduling_problem
from data.example_data import get_example_data

if __name__ == "__main__":
    machines, tasks = get_example_data()
    result = solve_scheduling_problem(machines, tasks)
    print(result)
