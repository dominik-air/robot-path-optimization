import os
import gzip
import shutil


def unzip_and_save(source: str, target: str) -> None:
    with gzip.open(source, "rb") as f_in:
        with open(target, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

def prepare_dataset(source_dir: str = "ALL_tsp", target_dir: str = "tsp_instances") -> None:
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    files = os.listdir(source_dir)
    for file in files:
        name, *_ = file.split(".")
        if f"{name}.opt.tour.gz" in files:
            unzip_and_save(f"{source_dir}/{name}.tsp.gz", f"{target_dir}/{name}.tsp")
            unzip_and_save(f"{source_dir}/{name}.opt.tour.gz", f"{target_dir}/{name}.opt.tour")
