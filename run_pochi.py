import os
from itertools import repeat
from multiprocessing import Pool, current_process

import numpy as np
import pandas as pd

import command_runner as cr
import csv_manager as cm
import project_inspector as pi
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


def get_similar_projects_pairs(threshold, num_of_pairs, similarity_data):
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


def multiproc_run_iteration(proj_pair_group, output_option):
    pid = current_process().pid
    temp_file_name = str(pid) + ".csv"
    cm.init_csv_file(temp_file_name, POCHI_OUTPUT_HEADER, MULTIPROC_TEMP_DIR)

    run_pochi_for_pairs_dataframe(
        pairs_dataframe=proj_pair_group,
        options=output_option,
        output_filename=temp_file_name,
        output_dir=MULTIPROC_TEMP_DIR,
    )


def run_multiproc(project_pairs, output_option):
    proj_pair_groups = np.array_split(project_pairs, 3)

    with Pool() as pool:
        pool.starmap(
            multiproc_run_iteration, zip(proj_pair_groups, repeat(output_option))
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


def pochi_extract_compare(
    project1,
    project2,
    project1_file_list,
    project2_file_list,
    software_location=BIRTHMARK_SOFTWARE,
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


def run_pochi_for_pairs_dataframe(
    pairs_dataframe,
    options=None,
    output_filename=POCHI_OUTPUT_FILENAME,
    output_dir=OUTPUT_DIR,
):
    for index, row in pairs_dataframe.iterrows():
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
            project1=row.project1,
            project2=row.project2,
            project1_ver=row.project1_ver,
            project2_ver=row.project2_ver,
            project1_file_list=project1_file_list,
            project2_file_list=project2_file_list,
            options=options,
            output_filename=output_filename,
            output_dir=output_dir,
        )


def run_pochi_for_similar_projects(output_option="no-csv", is_multiproc=False):
    similarity_groups = get_similar_projects_pairs(
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

    run_pochi_for_pairs_dataframe(pairs_dataframe=project_pairs, options=output_option)


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
        project1=project1,
        project2=project2,
        project1_ver=project1_version,
        project2_ver=project2_version,
        project1_file_list=project1_file_list,
        project2_file_list=project2_file_list,
        output_filename=output_filename,
        options=options,
    )


def run_pochi_for_all(
    dir, output_option=None, is_multiproc=False, distinct_projects=True
):
    project_files_data = []
    project_types = pi.get_project_types_list()

    for project_type in project_types:
        project_list = pi.get_project_list(TESTED_SOFTWARE_DIR, project_type)
        for project_name in project_list:
            version_list = pi.get_project_version_list(
                TESTED_SOFTWARE_DIR, project_name, project_type
            )
            for project_ver in version_list:
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
    pairs_df = create_project_pairs(df, distinct_projects)

    if is_multiproc:
        run_multiproc(pairs_df, output_option)
        # TODO: combine temp files
        return

    cm.init_csv_file(POCHI_OUTPUT_FILENAME, POCHI_OUTPUT_HEADER, OUTPUT_DIR)

    run_pochi_for_pairs_dataframe(pairs_dataframe=pairs_df, options=output_option)


def run_pochi_single_project(project_name, project_type):
    project_ver_list = pi.get_project_version_list(
        TESTED_SOFTWARE_DIR, project_name, project_type
    )
    project_files_data = []

    for ver in project_ver_list:
        new_entry = [
            project_name,
            project_type,
            ver,
        ]
        project_files_data.append(new_entry)

    df = pd.DataFrame(
        project_files_data,
        columns=["project", "project_type", "project_ver"],
    )
    pairs_df = create_project_pairs(df)

    output_filename = POCHI_VERSION + "_" + project_name + "_versions.csv"

    run_pochi_for_pairs_dataframe(
        pairs_dataframe=pairs_df, output_filename=output_filename
    )


def run_pochi_single_category(project_type):
    project_files_data = []
    project_list = pi.get_project_list(TESTED_SOFTWARE_DIR, project_type)

    for project_name in project_list:
        project_versions = pi.get_project_version_list(
            TESTED_SOFTWARE_DIR, project_name
        )
        for project_ver in project_versions:
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
    pairs_df = create_project_pairs(df)

    project_type = project_type.replace("/", "")
    output_filename = POCHI_VERSION + "_" + project_type + "_output.csv"

    run_pochi_for_pairs_dataframe(pairs_df, output_filename=output_filename)


def run_pochi_category_pair(project_type1, project_type2, distinct_projects=True):
    project_files_data = []
    project_list1 = pi.get_project_list(TESTED_SOFTWARE_DIR, project_type1)
    project_list2 = pi.get_project_list(TESTED_SOFTWARE_DIR, project_type2)

    for project_name in project_list1:
        project_versions = pi.get_project_version_list(
            TESTED_SOFTWARE_DIR, project_name
        )
        for project_ver in project_versions:
            new_entry = [
                project_name,
                project_type1,
                project_ver,
            ]
            project_files_data.append(new_entry)

    for project_name in project_list2:
        project_versions = pi.get_project_version_list(
            TESTED_SOFTWARE_DIR, project_name
        )
        for project_ver in project_versions:
            new_entry = [
                project_name,
                project_type2,
                project_ver,
            ]
            project_files_data.append(new_entry)

    df = pd.DataFrame(
        project_files_data,
        columns=["project", "project_type", "project_ver"],
    )
    pairs_df = create_project_pairs(df, distinct_projects)
    project_type1 = project_type1.replace("/", "")
    project_type2 = project_type2.replace("/", "")
    output_filename = "_".join(
        [POCHI_VERSION, project_type1, project_type2, "_output.csv"]
    )

    run_pochi_for_pairs_dataframe(
        pairs_dataframe=pairs_df, output_filename=output_filename
    )
