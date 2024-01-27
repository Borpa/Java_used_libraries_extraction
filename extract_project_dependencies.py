import csv
import io
import os
import re
import subprocess
import sys

import pandas as pd
from bs4 import BeautifulSoup


output_filename = "projects_dependencies.csv"


def init_output_csv(header, filename):
    """
    Initialize output csv file for extracted dependencies

    Parameters:
    ----------

    header : str
        The header of the output csv

    filename : str
        output csv filename

    """
    with open(filename, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def append_new_entry(filename, entry_list):
    """
    Append new values to the output csv file

    Parameters:
    ----------

    filename : str
        output csv filename

    entry_list : list(list(str))
        list of new entries to the output file

    """
    with open(filename, "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        for entry in entry_list:
            writer.writerow(entry)


def deps_extracted_check(output_filename, project_name):
    """
    Check if the dependencies have already been extracted
      from the project by checking the entries of the output file

    Parameters:
    ----------

    output_filename : str
        output csv filename

    project_name : str
        name of the project

    """
    df = pd.read_csv(output_filename)
    return project_name in df["project"].unique().tolist()


def get_project_type(filepath, type_list):
    """
    Get the type of the project from provided list of types.
    Returns "empty_project" if not found.

    Parameters:
    ----------

    filepath : str
        filepath to the project file

    type_list : list(str)
        list of possible project types

    """
    project_type = "/empty_type/"
    for typ in type_list:
        if typ in filepath:
            project_type = typ
            break
    return project_type


def create_entry_list(package_name, project_name, project_type, dep_list):
    """
    Create list of entries for the output csv file.

    Parameters:
    ----------
    package_name : str
        name of the package

    project_name : str
        name of the project

    project_type : str
        type of project

    dep_list : list(str)
        list of project's dependencies

    """
    entry_list = []
    for dep in dep_list:
        entry_list.append([package_name, project_name, dep, project_type])
    return entry_list


def run_cmd_command(command):
    """
    Run cmd command and return the output.

    Parameters:
    ----------

    command : str
        cmd command

    """
    proc = subprocess.Popen(
        command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    out, err = proc.communicate()
    output = out.decode()
    return output


def is_dep_local_check(dir_path, dep_name):
    """
    Check if the dependency is located in the project's directories.

    Parameters:
    ----------

    dir_path : str
        project's directory

    dep_name : str
        dependency name

    """
    check = False
    for root, dirs, files in os.walk(dir_path):
        root_dot_format = root.replace("/", ".").replace("\\", ".")
        check = dep_name in root_dot_format
        if check:
            break
    return check


def extract_deps_from_pom(filepath):
    """
    Extract dependencies from "pom.xml" file. Returns the set of dependencies.

    Parameters:
    ----------

    filepath: str
        path to the "pom.xml" file

    """
    with open(filepath, "r") as f:
        xml_data = f.read()
    bs_data = BeautifulSoup(xml_data, "xml")

    dep_list = []
    dir_path = filepath.replace("pom.xml", "")
    for dep in bs_data.find_all("dependency"):
        # dep_list.append({"dependency": dep.find("artifactId").text,
        #                 "version": dep.find("version").text})
        dep_name = dep.find("artifactId").text
        if not is_dep_local_check(dir_path, dep_name):
            dep_list.append(dep.find("artifactId").text)

    # print("extracted dependencies from {}".format(filepath))
    return set(dep_list)


def extract_deps_from_jar(filepath):
    """
    Extract dependencies from .jar file. Returns the set of dependencies.

    Parameters:
    ----------

    filepath: str
        path to the .jar file

    """
    jar_filename = os.path.basename(filepath)
    command = "jdeps -R --print-module-deps {}".format(filepath)
    output = run_cmd_command(command)

    if (
        "Error: Missing dependencies:" not in output
    ):  # check if .jar contains the dependencies
        command = "jdeps -R {}".format(filepath)
        output = run_cmd_command(command)

    buffer = io.StringIO(output)
    line = buffer.readline()

    dep_list = []

    while line:
        if "->" in line and "not found" in line or jar_filename in line:
            line = line.replace("->", "")
            entry = re.split("\s\s+", line)
            entry = [i for i in entry if i]  # remove empty elements

            if len(entry) != 3:
                line = (
                    buffer.readline()
                )  # skip lines without "<package> -> <dependency> <origin>" line
                continue

            dir_path = filepath.replace(jar_filename, "")

            # check if dependency is not included or if dependency is included in the .jar and is not standard
            if (
                entry[2] == "not found"
                or entry[2] == jar_filename
                and not entry[1].startswith("java.")
            ):
                if not is_dep_local_check(dir_path, entry[1]):
                    dep_list.append(entry[1])

        line = buffer.readline()

    # print("extracted dependencies from {}".format(filepath))
    return set(dep_list)


def get_project_name(filepath, project_types):
    project_name = filepath
    for type in project_types:
        if type in project_name:
            project_name_start = project_name.index(type) + len(type)
            project_name = project_name[project_name_start:]
            try:
                project_name_end = project_name.index("/")
                project_name = project_name[:project_name_end]
            except IndexError:
                project_name = project_name
            break
    return project_name


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Incorrect number of arguments\n")
        exit()

    target_dir = sys.argv[1]

    header = ["package", "project", "dependency", "project_type"]

    project_types = [
        "/ai_app/",
        "/book_reader/",
        "/web_file_browser/",
        "/calculator/",
        "/emulator_environment/",
        "/graphic_editor/",
        "/dev_environment/",
        "/media_player/",
        "/terminal_interface/",
        "/text_editor/",
        "/text_voice_chat/",
    ]
    dir_name_stopwords = ["src", "target", "lib"]

    init_output_csv(header, output_filename)

    for root, dirs, files in os.walk(target_dir):
        if "pom.xml" in files:
            file = "pom.xml"
            filepath = os.path.join(root, file).replace("\\", "/")

            package_name = os.path.basename(root)

            if package_name in dir_name_stopwords:
                continue

            project_name = get_project_name(filepath, project_types)

            if deps_extracted_check(output_filename, project_name):
                continue

            dep_list = extract_deps_from_pom(filepath)
            project_type = get_project_type(filepath, project_types)

            append_new_entry(
                output_filename,
                create_entry_list(package_name, project_name, project_type, dep_list),
            )
            continue

        for file in files:
            if file.endswith(".jar"):
                filepath = os.path.join(root, file).replace("\\", "/")

                package_name = os.path.basename(root)

                if package_name in dir_name_stopwords:
                    continue

                project_name = get_project_name(filepath, project_types)

                if deps_extracted_check(output_filename, project_name):
                    continue

                filename = file.replace(".jar", "")

                dep_list = extract_deps_from_jar(filepath)
                project_type = get_project_type(filepath, project_types)

                append_new_entry(
                    output_filename,
                    create_entry_list(
                        package_name, project_name, project_type, dep_list
                    ),
                )
