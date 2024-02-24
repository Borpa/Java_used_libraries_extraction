import os
from itertools import repeat
from multiprocessing import Pool, current_process, freeze_support

import numpy as np
import pandas as pd

import command_runner as cr
import csv_manager as cm
import project_inspector as pi
import run_stigmata as stigmata
from calculate_files_similarity import FILES_SIM
from extract_project_dependencies import TESTED_SOFTWARE_DIR

BIRTHMARK_SOFTWARE = "D:/Study/phd_research/birthmark_extraction_software/"

SIMILARITY_THRESHOLD = 70
SIMILARITY_PAIRS_NUM = 3

POCHI_VERSION = "pochi-2.6.0"
POCHI_OUTPUT_FILENAME = POCHI_VERSION + "_output_w_ver.csv"
OUTPUT_DIR = "birthmarks/"
MULTIPROC_TEMP_DIR = "temp/"
POCHI_OUTPUT_HEADER = [
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


# TODO: add version information in groupby method
def get_similar_pairs(threshold, num_of_pairs, similarity_data):
    df = pd.read_csv(similarity_data)
    project_groups = [
        x
        for _, x in df.groupby(["project1", "project2", "project1_ver", "project2_ver"])
    ]
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
    output_filename=POCHI_OUTPUT_FILENAME,
    output_dir=OUTPUT_DIR,
):
    full_path = software_location + POCHI_VERSION + "/bin/"
    pochi_script = "sh " + full_path + "pochi"
    extraction_script = "./pochi_scripts/" + "extract-compare.groovy"

    for project1_file in project1_file_list:
        for project2_file in project2_file_list:
            command = " ".join(
                [
                    pochi_script,
                    extraction_script,
                    project1_file,
                    project2_file,
                    # options,
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

            cm.append_csv_data(output_filename, file_pair_result, output_dir)


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
    pid = current_process().pid
    temp_file = str(pid) + ".csv"
    cm.init_csv_file(temp_file, POCHI_OUTPUT_HEADER, MULTIPROC_TEMP_DIR)

    for index, row in proj_pair_group.iterrows():
        project1_file_list = pi.get_project_jar_list(
            TESTED_SOFTWARE_DIR,
            row.project1_type,
            row.project1,
            row.project1_ver,
        )
        project2_file_list = pi.get_project_jar_list(
            TESTED_SOFTWARE_DIR,
            row.project2_type,
            row.project2,
            row.project2_ver,
        )

        pochi_extract_compare(
            BIRTHMARK_SOFTWARE,
            row.project1,
            project1_file_list,
            row.project2,
            project2_file_list,
            output_option,
            row.project1_ver,
            row.project2_ver,
            output_filename=temp_file,
            output_dir=MULTIPROC_TEMP_DIR,
        )


def run_multiproc(project_pairs, output_option):
    proj_pair_groups = np.array_split(project_pairs, 3)

    with Pool() as pool:
        pool.starmap(multiproc_run, zip(proj_pair_groups, repeat(output_option)))


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
        run_multiproc(project_pairs, output_option)
        return

    cm.init_csv_file(POCHI_OUTPUT_FILENAME, POCHI_OUTPUT_HEADER, OUTPUT_DIR)
    for index, row in project_pairs.iterrows():
        project1_file_list = pi.get_project_jar_list(
            TESTED_SOFTWARE_DIR, row.project1_type, row.project1
        )
        project2_file_list = pi.get_project_jar_list(
            TESTED_SOFTWARE_DIR, row.project2_type, row.project2
        )

        pochi_extract_compare(
            BIRTHMARK_SOFTWARE,
            row.project1,
            project1_file_list,
            row.project2,
            project2_file_list,
            output_option,
        )


def run_pochi_for_pair(
    project1,
    project1_type,
    project2,
    project2_type,
    options=None,
    project1_version=None,
    project2_version=None,
):
    project1_file_list = pi.get_project_jar_list(
        TESTED_SOFTWARE_DIR,
        project1_type,
        project1,
        project1_version,
    )
    project2_file_list = pi.get_project_jar_list(
        TESTED_SOFTWARE_DIR,
        project2_type,
        project2,
        project2_version,
    )
    output_filename = project1 + "_" + project2 + ".csv"
    cm.init_csv_file(output_filename, POCHI_OUTPUT_HEADER, OUTPUT_DIR)

    pochi_extract_compare(
        BIRTHMARK_SOFTWARE,
        project1,
        project1_file_list,
        project2,
        project2_file_list,
        options,
        project1_version,
        project2_version,
        output_filename=output_filename,
    )


def create_project_pairs(dataframe, distinct_projects=None):
    row_count = len(dataframe.index)
    column_names = [
        "project1",
        "project2",
        "project1_type",
        "project2_type",
        "project1_ver",
        "project2_ver",
    ]

    result_list = []

    for i in range(0, row_count):
        for j in range(1, row_count):
            if i == j:
                continue

            project1_line = dataframe.iloc[i]
            project2_line = dataframe.iloc[j]
            if distinct_projects is not None:
                if distinct_projects and project1_line.project == project2_line.project:
                    continue
                elif (
                    not distinct_projects
                    and project1_line.project != project2_line.project
                ):
                    continue

            newline = [
                project1_line.project,
                project2_line.project,
                project1_line.project_type,
                project2_line.project_type,
                project1_line.project_ver,
                project2_line.project_ver,
            ]

            mirrored_line = [
                project2_line.project,
                project1_line.project,
                project2_line.project_type,
                project1_line.project_type,
                project2_line.project_ver,
                project1_line.project_ver,
            ]

            if mirrored_line not in result_list:
                result_list.append(newline)

    result_df = pd.DataFrame(result_list, columns=column_names)

    return result_df


# TODO: add function to run extraction for all projects in a dir
def run_pochi_for_all(
    dir, output_option=None, is_multiproc=False, distinct_projects=None
):
    full_jar_list = pi.get_full_jar_list(dir)
    project_files_data = []
    for jar in full_jar_list:
        project_type = pi.get_project_type(jar)
        project_name = pi.get_project_name(jar)
        project_ver = pi.get_project_ver(jar, project_name)

        new_entry = [
            project_name,
            project_type,
            project_ver,
        ]

        project_files_data.append(new_entry)

    df = pd.DataFrame(
        project_files_data,
        columns=["project", "project_type", "project_ver"],
    )
    df = df.drop_duplicates()

    pairs_df = create_project_pairs(df, distinct_projects)

    if is_multiproc:
        run_multiproc(pairs_df, output_option)
        # TODO: combine temp files
        return

    cm.init_csv_file(POCHI_OUTPUT_FILENAME, POCHI_OUTPUT_HEADER, OUTPUT_DIR)

    for index, row in pairs_df.iterrows():
        project1_file_list = pi.get_project_jar_list(
            TESTED_SOFTWARE_DIR,
            row.project1_type,
            row.project1,
            row.project1_ver,
        )
        project2_file_list = pi.get_project_jar_list(
            TESTED_SOFTWARE_DIR,
            row.project2_type,
            row.project2,
            row.project2_ver,
        )
        pochi_extract_compare(
            software_location=BIRTHMARK_SOFTWARE,
            project1=row.project1,
            project1_file_list=project1_file_list,
            project2=row.project2,
            project2_file_list=project2_file_list,
            options=output_option,
            project1_ver=row.project1_ver,
            project2_ver=row.project2_ver,
        )


def run_pochi_single_project(project_name, project_type):
    project_file_list = pi.get_project_jar_list(
        TESTED_SOFTWARE_DIR, project_type, project_name
    )
    project_files_data = []

    for file in project_file_list:
        project_ver = pi.get_project_ver(file, project_name)
        new_entry = [
            project_name,
            project_type,
            project_ver,
        ]
        project_files_data.append(new_entry)

    df = pd.DataFrame(
        project_files_data,
        columns=["project", "project_type", "project_ver"],
    )
    df = df.drop_duplicates()
    pairs_df = create_project_pairs(df)

    output_filename = project_name + "_versions.csv"

    for index, row in pairs_df.iterrows():
        project1_file_list = pi.get_project_jar_list(
            TESTED_SOFTWARE_DIR,
            row.project1_type,
            row.project1,
            row.project1_ver,
        )
        project2_file_list = pi.get_project_jar_list(
            TESTED_SOFTWARE_DIR,
            row.project2_type,
            row.project2,
            row.project2_ver,
        )
        pochi_extract_compare(
            software_location=BIRTHMARK_SOFTWARE,
            project1=row.project1,
            project1_file_list=project1_file_list,
            project2=row.project2,
            project2_file_list=project2_file_list,
            project1_ver=row.project1_ver,
            project2_ver=row.project2_ver,
            output_filename=output_filename,
        )


def run_pochi_single_category():
    return None


def run_pochi_category_pair():
    return None


def main():
    # run_pochi_for_similar_proj()

    # project1 = "FrankCYB_JavaGPT"
    # project1_type = "/ai_app/"
    # project1_ver = "v1.3.2"
    # project2 = "LiLittleCat_ChatGPT"
    # project2_type = "/ai_app/"
    # project2_ver = "v1.0.3"
    # output = run_pochi_for_pair(
    #    project1,
    #    project1_type,
    #    project2,
    #    project2_type,
    #    project1_version=project1_ver,
    #    project2_version=project2_ver,
    # )
    # output_filename = project1 + "_" + project2 + ".csv"

    #run_pochi_for_all(dir=TESTED_SOFTWARE_DIR, is_multiproc=True)
    run_pochi_single_project("pH-7_Simple-Java-Calculator", "/calculator/")


if __name__ == "__main__":
    freeze_support()
    main()
