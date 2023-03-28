import os
import time
import lkh
import tsplib95
import pandas as pd
import ortools_utils
import ga_utils
import concorde_utils
from typing import NamedTuple


class ExperimentResult(NamedTuple):
    time: float
    score: int
    solver: str
    problem: str


def setup_test_case_for_lkh(problem_path: str):
    with open(problem_path) as f:
        data = f.read()
    return lkh.LKHProblem.parse(data)


def lkh_test(problem):
    return lkh.solve(solver="LKH-3.0.7/LKH", problem=problem, max_trials=10000, runs=1)


def setup_test_case_for_ortools(problem_path: str):
    problem = tsplib95.load(problem_path)
    G = problem.get_graph()
    return ortools_utils.create_distance_matrix_from_graph(G)


def ortools_test(matrix):
    return ortools_utils.run_ortools(matrix)


def test_ortools(problem_path: str, niter: int) -> list[ExperimentResult]:
    matrix = setup_test_case_for_ortools(problem_path)
    results = []
    problem_name = problem_path.split("/")[-1]
    for _ in range(niter):
        start_time = time.perf_counter()
        dist = ortools_test(matrix)
        end_time = time.perf_counter()
        results.append(
            ExperimentResult(
                time=(end_time - start_time),
                score=int(dist),
                solver="ortools",
                problem=problem_name,
            )
        )
    return results


def test_lkh(problem_path: str, niter: int) -> list[ExperimentResult]:
    problem = setup_test_case_for_lkh(problem_path)
    results = []
    problem_name = problem_path.split("/")[-1]
    for _ in range(niter):
        start_time = time.perf_counter()
        route = lkh_test(problem)
        end_time = time.perf_counter()
        try:
            score = problem.trace_tours(route)[0]
        except IndexError:
            route = route[0]
            route = [r - 1 for r in route]
            score = problem.trace_tours([route])[0]
        results.append(
            ExperimentResult(
                time=(end_time - start_time),
                score=int(score),
                solver="lkh",
                problem=problem_name,
            )
        )
    return results


def test_ga(problem_path: str, niter: int) -> list[ExperimentResult]:
    results = []
    problem_name = problem_path.split("/")[-1]
    for _ in range(niter):
        start_time = time.perf_counter()
        dist = ga_utils.run_ga(problem_path)
        end_time = time.perf_counter()
        results.append(
            ExperimentResult(
                time=(end_time - start_time),
                score=int(dist),
                solver="eax",
                problem=problem_name,
            )
        )
    ga_utils.clean_up_after_ga()
    return results


def test_concorde(problem_path: str, niter: int) -> list[ExperimentResult]:
    results = []
    problem_name = problem_path.split("/")[-1]
    for _ in range(niter):
        start_time = time.perf_counter()
        dist = concorde_utils.run_concorde(problem_path)
        end_time = time.perf_counter()
        results.append(
            ExperimentResult(
                time=(end_time - start_time),
                score=int(dist),
                solver="concorde",
                problem=problem_name,
            )
        )
    concorde_utils.clean_up_after_concorde()
    return results

def run_test_suite(dir_with_test_cases: str, output_file: str) -> None:
    problem_paths = [
        f"{dir_with_test_cases}/{p}" for p in os.listdir(dir_with_test_cases) if p.endswith(".tsp")
    ]
    niter = 100
    data = []
    experiments_start_time = time.perf_counter()
    ga_skipped = 0
    for path in problem_paths:
        skip_ga = False
        try:
            ga_utils.run_ga(path)
        except:
            ga_skipped += 1
            skip_ga = True
        data += test_ortools(path, niter)
        data += test_lkh(path, niter)
        if not skip_ga:
            data += test_ga(path, niter)
        data += test_concorde(path, niter)
    experiments_end_time = time.perf_counter()
    print(f"Experiments took: {experiments_end_time-experiments_start_time}s.")
    print(f"GA skipped: {ga_skipped} problems out of: {len(problem_paths)}.")
    df = pd.DataFrame(data, columns=["time", "score", "solver", "problem"])
    df.to_csv(output_file)
if __name__ == "__main__":
    run_test_suite("custom_tsplibs", output_file="long_custom_benchmark_results.csv")