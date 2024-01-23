import os
import subprocess
import sys

import pandas as pd


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
    proc = subprocess.Popen(
        command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    out, err = proc.communicate()
    output = out.decode()
    return output


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
    extraction_script = "pochi_scripts/extract-compare_all.groovy"
    pochi_script = full_path + "pochi"
    total_output = []

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
            output = run_cmd_command(command)
            total_output.append(output)

    return total_output


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
                    jar_list.append(file)
    return jar_list


if __name__ == "__main__":
    option = sys.argv[0]

    similarity_data = "file_similarity.csv"
    birthmark_software = "../birthmark_extraction_software/"
    tested_software = "../tested_software/"

    pochi_output_header = [
        "birthmark",
        "comparator",
        "matcher",
        "file1",
        "file2",
        "result",
    ]

    similarity_groups = get_similar_pairs(70, 3, similarity_data)
    project_pairs = similarity_groups[
        ["project1", "project2", "project1_type", "project2_type"]
    ]
    project_pairs = project_pairs.drop_duplicates()

    print(project_pairs)

    for index, row in project_pairs.iterrows():
        project1_list = get_project_jar_list(
            tested_software, row.project1_type, row.project1
        )
        project2_list = get_project_jar_list(
            tested_software, row.project2_type, row.project2
        )

        output = run_pochi(
            birthmark_software,
            row.project1,
            project1_list,
            row.project2,
            project2_list,
            "no-csv",
        )
