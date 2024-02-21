import io
import os
import re

import pandas as pd
from bs4 import BeautifulSoup

import command_runner as cr
import csv_manager as cm
import project_inspector as pi

TESTED_SOFTWARE_DIR = "D:/Study/phd_research/test_projects/"
PROJECTS_DEP = "projects_dependencies.csv"
DEP_DIR = "./dependencies/"


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


def create_entry_list(package_name, project_name, project_ver, project_type, dep_list):
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
        entry_list.append([package_name, project_name, project_ver, project_type, dep])
    return entry_list


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
    output = cr.run_cmd_command(command)

    if (
        "Error: Missing dependencies:" not in output
    ):  # check if .jar contains the dependencies
        command = "jdeps -R {}".format(filepath)
        output = cr.run_cmd_command(command)

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


def get_project_ver(filepath, project_name):
    project_ver_start = filepath.index(project_name) + len(project_name)
    project_ver = filepath[project_ver_start:]
    try:
        project_ver_end = project_ver.index("/")
        project_ver = project_ver[:project_ver_end]
    except IndexError:
        project_ver = project_ver
    return project_ver


def main():
    header = ["package", "project", "project_ver", "project_type", "dependency"]

    dir_name_stopwords = ["src", "lib", ".mvn"]

    cm.init_csv_file(PROJECTS_DEP, header, DEP_DIR)

    for root, dirs, files in os.walk(TESTED_SOFTWARE_DIR):
        if "pom.xml" in files:
            file = "pom.xml"
            filepath = os.path.join(root, file).replace("\\", "/")

            package_name = os.path.basename(root)

            if package_name in dir_name_stopwords:
                continue

            project_name = pi.get_project_name(filepath)

            if deps_extracted_check(PROJECTS_DEP, project_name):
                continue

            dep_list = extract_deps_from_pom(filepath)
            project_type = pi.get_project_type(filepath)
            project_ver = pi.get_project_ver(filepath, project_name)

            cm.append_csv_data(
                PROJECTS_DEP,
                create_entry_list(
                    package_name, project_name, project_ver, project_type, dep_list
                ),
                DEP_DIR,
            )
            continue

        for file in files:
            if file.endswith(".jar"):
                filepath = os.path.join(root, file).replace("\\", "/")

                package_name = os.path.basename(root)

                if package_name in dir_name_stopwords:
                    continue

                project_name = pi.get_project_name(filepath)

                if deps_extracted_check(PROJECTS_DEP, project_name):
                    continue

                dep_list = extract_deps_from_jar(filepath)
                project_type = pi.get_project_type(filepath)
                project_ver = pi.get_project_ver(filepath, project_name)

                cm.append_csv_data(
                    PROJECTS_DEP,
                    create_entry_list(
                        package_name, project_name, project_ver, project_type, dep_list
                    ),
                    DEP_DIR,
                )


if __name__ == "__main__":
    main()
