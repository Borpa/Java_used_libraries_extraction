import os
from itertools import repeat
from multiprocessing import Pool, freeze_support

import numpy as np
import pandas as pd

import command_runner as cr
import csv_manager as cm
import project_inspector as pi
import run_stigmata as stigmata
from calculate_files_similarity import FILES_SIM

BIRTHMARK_SOFTWARE = "D:/Study/phd_research/birthmark_extraction_software/"
TESTED_SOFTWARE_DIR = "D:/Study/phd_research/test_software/"

SIMILARITY_THRESHOLD = 70
SIMILARITY_PAIRS_NUM = 3

POCHI_VERSION = "pochi-2.6.0"
POCHI_OUTPUT_FILENAME = POCHI_VERSION + "_output.csv"
OUTPUT_DIR = "birthmarks/"


# TODO: add version information in groupby method
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


def pochi_extract_compare(
    software_location,
    project1,
    project1_file_list,
    project2,
    project2_file_list,
    options=None,
    project1_ver=None,
    project2_ver=None,
):
    full_path = software_location + POCHI_VERSION + "/bin/"
    pochi_script = "sh " + full_path + "pochi"
    extraction_script = "pochi_scripts/" + "extract-compare.groovy"
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
            output = cr.run_bash_command(command)

            output = output.split("\r\n")
            file_pair_result = []

            for line in output:
                if len(line) == 0:
                    continue
                line = line.replace("\r\n", "").split(",")
                newline = [
                    project1,
                    project2,
                    project1_ver,
                    project2_ver,
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
    output = cr.run_bash_command(command).split("\r\n")

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


def multiproc_run(proj_pair_group, output_option):
    result = []
    for index, row in proj_pair_group.iterrows():
        project1_file_list = pi.get_project_jar_list(
            TESTED_SOFTWARE_DIR, row.project1_type, row.project1
        )
        project2_file_list = pi.get_project_jar_list(
            TESTED_SOFTWARE_DIR, row.project2_type, row.project2
        )

        output = pochi_extract_compare(
            BIRTHMARK_SOFTWARE,
            row.project1,
            project1_file_list,
            row.project2,
            project2_file_list,
            output_option,
        )
        result.append(output)

    return result


def run_multiproc(project_pairs, output_option):
    proj_pair_groups = np.array_split(project_pairs, 4)

    with Pool() as pool:
        result = pool.starmap(
            multiproc_run, zip(proj_pair_groups, repeat(output_option))
        )

    return result


def run_pochi_for_similar_proj(output_option="no-csv", is_multiproc=False):
    similarity_groups = get_similar_pairs(
        SIMILARITY_THRESHOLD, SIMILARITY_PAIRS_NUM, FILES_SIM
    )
    project_pairs = similarity_groups[
        [
            "project1",
            "project2",
            "project1_type",
            "project2_type",
            "project1_ver",
            "project2_ver",
        ]
    ]
    project_pairs = (
        project_pairs.drop_duplicates()
    )  # might count num of pairs with similarity >= thershold in the future

    if is_multiproc:
        result = run_multiproc(project_pairs, output_option)
        return result

    total_output = []
    for index, row in project_pairs.iterrows():
        project1_file_list = pi.get_project_jar_list(
            TESTED_SOFTWARE_DIR, row.project1_type, row.project1
        )
        project2_file_list = pi.get_project_jar_list(
            TESTED_SOFTWARE_DIR, row.project2_type, row.project2
        )

        output = pochi_extract_compare(
            BIRTHMARK_SOFTWARE,
            row.project1,
            project1_file_list,
            row.project2,
            project2_file_list,
            output_option,
        )

        total_output += output

    return total_output


# TODO: add ver information
def run_pochi_for_pair(
    project1, project1_type, project2, project2_type, options="no-csv"
):
    project1_versions = None
    project2_versions = None

    project1_file_list = pi.get_project_jar_list(
        TESTED_SOFTWARE_DIR, project1_type, project1
    )
    project2_file_list = pi.get_project_jar_list(
        TESTED_SOFTWARE_DIR, project2_type, project2
    )

    output = pochi_extract_compare(
        BIRTHMARK_SOFTWARE,
        project1,
        project1_file_list,
        project2,
        project2_file_list,
        options,
    )
    return output


def create_project_pairs(dataframe):
    row_count = len(dataframe.index)
    column_names = [
        "project1_name",
        "project1_type",
        "project1_ver",
        "project1_file",
        "project2_name",
        "project2_type",
        "project2_ver",
        "project2_file",
    ]
    result_list = []

    for i in range(0, row_count):
        for j in range(1, row_count):
            if i == j:
                continue

            project1_line = dataframe.iloc[i]
            project2_line = dataframe.iloc[j]

            project1_part = [
                project1_line.project_name,
                project1_line.project_type,
                project1_line.project_ver,
                project1_line.jar,
            ]

            project2_part = [
                project2_line.project_name,
                project2_line.project_type,
                project2_line.project_ver,
                project2_line.jar,
            ]

            newline = project1_part + project2_part
            mirrored_line = project2_part + project1_part

            if mirrored_line not in result_list:
                result_list.append(newline)

    result_df = pd.DataFrame(result_list, columns=column_names)

    return result_df


# TODO: add function to run extraction for all projects in a dir
def run_pochi_for_all(dir, output_option="no-csv", is_multiproc=False):
    full_jar_list = pi.get_full_jar_list(dir)
    project_files_data = []
    for jar in full_jar_list:
        project_type = pi.get_project_type(jar)
        project_name = pi.get_project_name(jar)
        project_ver = pi.get_project_ver(jar, project_name)
        project_files_data.append(
            [
                project_name,
                project_type,
                project_ver,
                jar,
            ]
        )

    df = pd.DataFrame(
        project_files_data,
        columns=["project_name", "project_type", "project_ver", "jar"],
    )

    pairs_df = create_project_pairs(df)

    if is_multiproc:
        result = run_multiproc(pairs_df, output_option)
        return result

    total_output = []
    for index, row in pairs_df.iterrows():
        output = pochi_extract_compare(
            software_location=BIRTHMARK_SOFTWARE,
            project1=row.project1_name,
            project1_file_list=[row.project1_file],
            project2=row.project2_name,
            project2_file_list=[row.project2_file],
            options=output_option,
            project1_ver=row.project1_ver,
            project2_ver=row.project2_ver,
        )
        total_output += output

    return total_output


def main():
    pochi_output_header = [
        "project1",
        "project2",
        "project1_ver",
        "project2_ver",
        "project1_file",
        "project2_file",
        "birthmark",
        "comparator",
        "matcher",
        "class1",
        "class2",
        "similarity",
    ]
    # run_pochi_for_similar_proj()
    project1 = "Cypher-Notepad-master"
    project1_type = "/text_editor/"
    project2 = "ChatGPT-1.0.2"
    project2_type = "/ai_app/"
    option = "fuc"
    output = run_pochi_for_pair(
        project1, project1_type, project2, project2_type, option
    )
    output_filename = project1 + "_" + project2 + ".csv"

    cm.init_csv_file(output_filename, pochi_output_header, OUTPUT_DIR)
    for row in output:
        cm.append_csv_data(output_filename, row, OUTPUT_DIR)


if __name__ == "__main__":
    freeze_support()
    main()
