import os

import pandas as pd

import csv_manager as cm
import project_inspector as pi
from birthmark_extraction import TESTED_SOFTWARE_DIR

PROJECTS_DEP_FILE = "projects_dependencies.csv"
OUTPUT_FILENAME = "files_dependencies.csv"


def get_project_type_from_file(dep_filename, project_name):
    df = pd.read_csv(dep_filename)
    try:
        type = df[df.project == project_name].iloc[0]["project_type"]
    except IndexError:
        type = None
    return type


def extract_files_external_deps(filepath, project_path, dep_filename):
    project_name = os.path.basename(project_path)
    project_deps = pi.get_project_external_deps(dep_filename, project_name)
    external_deps = []

    with open(filepath, "r", errors="replace") as f:
        line = f.readline()
        while line:
            if "{" in line:
                break
            if "import " in line and "=" not in line:
                line = line.replace("import ", "").replace("static ", "")
                line = line.replace(";\n", "")

                for dep in project_deps:
                    if dep in line:
                        external_deps.append(line)
            line = f.readline()
    return external_deps


def main():
    header = ["filename", "type", "project", "project_ver", "dependencies", "filepath"]

    cm.init_csv_file(header, OUTPUT_FILENAME)

    project_list = pi.get_projects_path_list(TESTED_SOFTWARE_DIR)

    for project in project_list:
        # TODO: add function to get the list of versions
        project_files = pi.get_projects_filelist(project)
        for file in project_files:
            filename = os.path.basename(file)
            filepath = file
            project_name = pi.get_project_name(filepath)
            project_ver = pi.get_project_ver(filepath, project_name)

            project_type = get_project_type_from_file(PROJECTS_DEP_FILE, project_name)
            if project_type is None:
                continue

            dependencies = extract_files_external_deps(file, project, PROJECTS_DEP_FILE)
            if len(dependencies) == 0:
                continue
            new_entry = [
                filename,
                project_type,
                project_name,
                project_ver,
                dependencies,
                filepath,
            ]
            cm.append_single_entry(OUTPUT_FILENAME, new_entry)


if __name__ == "__main__":
    main()
