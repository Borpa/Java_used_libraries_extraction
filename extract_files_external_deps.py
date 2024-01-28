import csv
import os
import sys

import pandas as pd

PROJECTS_DEP_FILE = "projects_dependencies.csv"
OUTPUT_FILENAME = "files_dependencies.csv"


def init_output_csv(header, filename):
    with open(filename, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def append_new_entry(filename, entry):
    with open(filename, "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(entry)


def get_project_external_deps(dep_filename, project_name):
    df = pd.read_csv(dep_filename)
    external_deps = df.loc[df["project"] == project_name]["dependency"].tolist()
    return external_deps


def get_project_type(dep_filename, project_name):
    df = pd.read_csv(dep_filename)
    try:
        type = df[df.project == project_name].iloc[0]["project_type"]
    except IndexError:
        type = None
    return type


def get_projects_path_list(target_dir):
    project_list = []
    dirs_flag = True
    for root, dirs, files in os.walk(target_dir):
        depth = root[len(target_dir) + len(os.path.sep) :].count(os.path.sep)
        if depth == 0:
            if dirs_flag:
                dirs_flag = False  # skip first entry that contains names of the directories from upper level
                continue
            for dir in dirs:
                project_path = os.path.join(root, dir).replace("\\", "/")
                project_list.append(project_path)
        if depth != 0:
            continue
    return project_list


def get_projects_filelist(project_path):
    filelist = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith(".java"):
                filepath = os.path.join(root, file).replace("\\", "/")
                filelist.append(filepath)
    return filelist


def extract_files_external_deps(filepath, project_path, dep_filename):
    project_name = os.path.basename(project_path)
    project_deps = get_project_external_deps(dep_filename, project_name)
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Incorrect number of arguments\n")
        exit()
    target_dir = sys.argv[1]

    header = ["filename", "type", "project", "dependencies", "filepath"]

    init_output_csv(header, OUTPUT_FILENAME)

    project_list = get_projects_path_list(target_dir)

    for project in project_list:
        project_files = get_projects_filelist(project)
        for file in project_files:
            filename = os.path.basename(file)
            filepath = file
            project_name = os.path.basename(project)
            project_type = get_project_type(PROJECTS_DEP_FILE, project_name)
            if project_type is None:
                continue
            dependencies = extract_files_external_deps(file, project, PROJECTS_DEP_FILE)
            if len(dependencies) == 0:
                continue
            new_entry = [filename, project_type, project_name, dependencies, filepath]
            append_new_entry(OUTPUT_FILENAME, new_entry)
