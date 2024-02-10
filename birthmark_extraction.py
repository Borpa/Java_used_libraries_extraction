import csv
import os
import subprocess
import sys

import pandas as pd

import run_stigmata as stigmata

GIT_BASH_EXEC_PATH = "C:/Program Files/Git/bin/bash.exe"

SIMILARITY_DATA = "file_similarity.csv"
BIRTHMARK_SOFTWARE = "D:/Study/phd_research/birthmark_extraction_software/"
TESTED_SOFTWARE = "D:/Study/phd_research/tested_software/"

SIMILARITY_THRESHOLD = 70
SIMILARITY_PAIRS_NUM = 3

POCHI_VERSION = "pochi-2.6.0"
POCHI_OUTPUT_FILENAME = POCHI_VERSION + "_output.csv"
OUTPUT_DIR = "birthmarks/"


def get_similar_pairs(threshold, num_of_pairs, similarity_data):
    df = pd.read_csv(similarity_data)
    project_groups = [x for _, x in df.groupby(["project1", "project2"])]
    top_results = []

    for group in project_groups:
        group = (
            group.loc[group["dependency_ratio"] >= threshold]
            .sort_values(by="dependency_ratio", ascending=False)
            .head(num_of_pairs)
        )
        top_results.append(group)

    return pd.concat(top_results)


def run_bash_command(command):
    output = subprocess.check_output(
        command, shell=False, executable=GIT_BASH_EXEC_PATH
    )
    output = output.decode()

    return output


def init_csv_file(filename, header, dir=None):
    if dir is not None:
        if not os.path.exists(dir):
            os.makedirs(dir)
        filename = dir + filename
    with open(filename, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def append_csv_data(filename, data, dir=None):
    filename = dir + filename
    with open(filename, "a", encoding="UTF8", newline="") as f:
        for row in data:
            writer = csv.writer(f)
            writer.writerow(row)


def pochi_extract_compare_all(
    software_location,
    project1,
    project1_file_list,
    project2,
    project2_file_list,
    options=None,
):
    full_path = software_location + POCHI_VERSION + "/bin/"
    pochi_script = "sh " + full_path + "pochi"
    extraction_script = full_path + "extract_test_2.groovy"
    total_result = []

    for project1_file in project1_file_list:
        for project2_file in project2_file_list:
            command = " ".join(
                [
                    pochi_script,
                    extraction_script,
                    project1_file,
                    project2_file,
                    options,
                ]
            )
            output = run_bash_command(command)

            output = output.split("\r\n")
            file_pair_result = []

            for line in output:
                if len(line) == 0:
                    continue
                line = line.replace("\r\n", "").split(",")
                newline = [
                    project1,
                    project2,
                    os.path.basename(project1_file),
                    os.path.basename(project2_file),
                ] + line
                file_pair_result.append(newline)
            total_result.append(file_pair_result)

    return total_result


def pochi_extract_birthmark(software_location, project_file, birthmark):
    full_path = software_location + POCHI_VERSION + "/bin/"
    pochi_script = "sh " + full_path + "pochi"
    extraction_script = "pochi_scripts/" + "extract_birthmark.groovy"
    command = " ".join(
        [
            pochi_script,
            extraction_script,
            birthmark,
            project_file,
        ]
    )
    output = run_bash_command(command).split("\r\n")

    return output


def run_stigmata(
    project1,
    project1_file_list,
    project2,
    project2_file_list,
    options=None,
):
    total_result = []
    for project1_file in project1_file_list:
        for project2_file in project2_file_list:
            # pair_result = stigmata.extract_compare_all(project1_file, project2_file)
            pair_result = stigmata.extract_compare(
                "kgram", project1_file, project2_file
            )
            total_result.append(pair_result)

    return total_result


def get_project_jar_list(main_dir, project_type, project_name):
    project_type = project_type.replace("/", "")
    target_dir = main_dir + project_type + "/" + project_name + "/"
    jar_list = []

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".jar"):
                if "src" not in root and "lib" not in root:
                    filepath = os.path.join(root, file).replace("\\", "/")
                    jar_list.append(filepath)
    return jar_list


def main():
    output_option = "no-csv"
    if len(sys.argv) > 0:
        output_option = sys.argv[0]

    pochi_output_header = [
        "project1",
        "project2",
        "project1_file",
        "project2_file",
        "birthmark",
        "comparator",
        "matcher",
        "class1",
        "class2",
        "similarity",
    ]

    similarity_groups = get_similar_pairs(
        SIMILARITY_THRESHOLD, SIMILARITY_PAIRS_NUM, SIMILARITY_DATA
    )
    project_pairs = similarity_groups[
        ["project1", "project2", "project1_type", "project2_type"]
    ]
    project_pairs = (
        project_pairs.drop_duplicates()
    )  # might count num of pairs with similarity >= thershold in the future

    init_csv_file(POCHI_OUTPUT_FILENAME, pochi_output_header, OUTPUT_DIR)

    for index, row in project_pairs.iterrows():
        project1_file_list = get_project_jar_list(
            TESTED_SOFTWARE, row.project1_type, row.project1
        )
        project2_file_list = get_project_jar_list(
            TESTED_SOFTWARE, row.project2_type, row.project2
        )

        output = pochi_extract_compare_all(
            BIRTHMARK_SOFTWARE,
            row.project1,
            project1_file_list,
            row.project2,
            project2_file_list,
            output_option,
        )

        for row in output:
            append_csv_data(POCHI_OUTPUT_FILENAME, row, OUTPUT_DIR)


if __name__ == "__main__":
    main()
