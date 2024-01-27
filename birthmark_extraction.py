import csv
import os
import subprocess
import sys

import pandas as pd


git_bash_exec_path = "C:/Program Files/Git/bin/bash.exe"

similarity_data = "file_similarity.csv"
birthmark_software = "D:/Study/phd_research/birthmark_extraction_software/"
tested_software = "D:/Study/phd_research/tested_software/"

similarity_threshold = 70
similarity_pairs_num = 3

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


def run_cmd_command(command):
    output = subprocess.check_output(
        command, shell=False, executable=git_bash_exec_path
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


def run_pochi(
    software_location,
    project1,
    project1_file_list,
    project2,
    project2_file_list,
    options=None,
):
    version = "pochi-2.6.0"
    full_path = software_location + version + "/bin/"
    pochi_script = "sh " + full_path + "pochi"
    extraction_script = full_path + "extract_test_2.groovy"
    output_filename = "__".join([project1, project2]) + ".csv"
    output_dir = "birthmarks/"

    header = [
        "project1_file",
        "project2_file",
        "birthmark",
        "comparator",
        "matcher",
        "class1",
        "class2",
        "similarity",
    ]
    init_csv_file(output_filename, header, dir=output_dir)

    for project1_file in project1_file_list:
        for project2_file in project2_file_list:
            pair_output = []

            command = " ".join(
                [
                    pochi_script,
                    extraction_script,
                    project1_file,
                    project2_file,
                    options,
                ]
            )
            output = run_cmd_command(command)

            output = output.split("\r\n")
            for line in output:
                if len(line) == 0:
                    continue
                line = line.replace("\r\n", "").split(",")
                newline = [
                    os.path.basename(project1_file),
                    os.path.basename(project2_file),
                ] + line
                pair_output.append(newline)
            append_csv_data(output_filename, pair_output, output_dir)


def run_stigmara(software_location, program_1, program_2, options):
    version = "stigmata-master/target/"
    full_path = software_location + version

    return None


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


if __name__ == "__main__":
    output_option = "no-csv"
    if len(sys.argv) > 0:
        output_option = sys.argv[0]

    pochi_output_header = [
        "birthmark",
        "comparator",
        "matcher",
        "file1",
        "file2",
        "result",
    ]

    similarity_groups = get_similar_pairs(similarity_threshold, similarity_pairs_num, similarity_data)
    project_pairs = similarity_groups[
        ["project1", "project2", "project1_type", "project2_type"]
    ]
    project_pairs = project_pairs.drop_duplicates() # might count num of pairs with similarity >= thershold in the future

    for index, row in project_pairs.iterrows():
        project1_file_list = get_project_jar_list(
           tested_software, row.project1_type, row.project1
        )
        project2_file_list = get_project_jar_list(
           tested_software, row.project2_type, row.project2
        )

        output = run_pochi(
            birthmark_software,
            row.project1,
            project1_file_list,
            row.project2,
            project2_file_list,
            output_option,
        )
