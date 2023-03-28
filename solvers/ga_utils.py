import re
import os
import subprocess

def run_ga(problem_path: str, max_trials: int = 5, population_size: int = 100, offspring_size: int = 30) -> int:
    proc = subprocess.Popen(["bash", "GA-for-TSP/src/run.sh"], 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE)
    command = f"{problem_path}\n{max_trials}\n{population_size}\n{offspring_size}\n"
    result, err = proc.communicate(command.encode('ascii')) 
    pattern = re.compile(r"val = (?P<dist>\d+)")
    return int(pattern.search(result.decode("utf-8")).group("dist"))


def clean_up_after_ga() -> None:
    unwanted_files = {"a.out", "bestSolution.txt"}
    for file in os.listdir(os.getcwd()):
        if file in unwanted_files:
            os.remove(file)

