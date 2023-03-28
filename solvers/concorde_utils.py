import re
import os
import subprocess


def run_concorde(problem_path: str) -> float:
    result = subprocess.run(
        ["concorde/TSP/concorde", problem_path], stdout=subprocess.PIPE
    )
    pattern = re.compile(r"Optimal Solution: (?P<dist>\d+.\d+)")
    return float(pattern.search(result.stdout.decode("utf-8")).group("dist"))

def get_path_indices(problem_name: str) -> list[int]:
    with open(f"{problem_name}.sol") as f:
        path = f.readlines()[1].split()
    return [int(idx) for idx in path]

def clean_up_after_concorde() -> None:
    unwanted_extensions = {"sav", "mas", "sol", "pul", "res"}
    for file in os.listdir(os.getcwd()):
        extension = file.split(".")[-1]
        if extension in unwanted_extensions:
            os.remove(file)
