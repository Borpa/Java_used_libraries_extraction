import os
import gc
from itertools import repeat
from multiprocessing import Pool, current_process

import numpy as np
import pandas as pd

import command_runner as cr
import csv_manager as cm
import project_inspector as pi
from calculate_files_similarity import FILES_SIM
from extract_project_dependencies import TESTED_SOFTWARE_DIR


BIRTHMARK_SOFTWARE = "C:/Users/FedorovNikolay/source/Study/birthmark_extraction_software/"

SIMILARITY_THRESHOLD = 70
SIMILARITY_PAIRS_NUM = 3

POCHI_VERSION = "pochi-2.6.0"
POCHI_OUTPUT_FILENAME = POCHI_VERSION + "_output_w_ver.csv"
OUTPUT_DIR = "birthmarks/"
MULTIPROC_TEMP_DIR = "./temp/"
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


def __get_similar_projects_pairs(threshold, num_of_pairs, similarity_data):
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


def __combine_temp_files(temp_dir=MULTIPROC_TEMP_DIR):
    temp_files = os.listdir(temp_dir)
    df_list = []

    for temp_file in temp_files:
        df = pd.read_csv(temp_dir + temp_file)
        df_list.append(df)
    result_df = pd.concat(df_list)

    return result_df


def __drop_temp_files(temp_dir=MULTIPROC_TEMP_DIR):
    temp_files = os.listdir(temp_dir)
    for temp_file in temp_files:
        os.remove(temp_dir + temp_file)


def __multiproc_run_iteration_script_output(proj_pair_group, output_option):
    pid = current_process().pid
    temp_file_name = str(pid) + ".csv"
    # cm.init_csv_file(temp_file_name, POCHI_OUTPUT_HEADER, MULTIPROC_TEMP_DIR)

    run_pochi_pairs_dataframe_script_output(
        pairs_dataframe=proj_pair_group,
        options=output_option,
        output_filename=temp_file_name,
        output_dir=MULTIPROC_TEMP_DIR,
    )


def __multiproc_run_iteration(proj_pair_group, output_option):
    pid = current_process().pid
    temp_file_name = str(pid) + ".csv"
    cm.init_csv_file(temp_file_name, POCHI_OUTPUT_HEADER, MULTIPROC_TEMP_DIR)

    run_pochi_pairs_dataframe(
        pairs_dataframe=proj_pair_group,
        options=output_option,
        output_filename=temp_file_name,
        output_dir=MULTIPROC_TEMP_DIR,
    )


def __run_multiproc_script_output(project_pairs, output_option=None):
    proj_pair_groups = np.array_split(project_pairs, 3)

    with Pool() as pool:
        pool.starmap(
            __multiproc_run_iteration_script_output,
            zip(proj_pair_groups, repeat(output_option)),
        )


def __run_multiproc(project_pairs, output_option=None):
    proj_pair_groups = np.array_split(project_pairs, 3)

    with Pool() as pool:
        pool.starmap(
            __multiproc_run_iteration, zip(proj_pair_groups, repeat(output_option))
        )


def __create_project_pairs(dataframe, distinct_projects=None):
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


def pochi_extract_compare_script_output(
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
                    ">",
                    output_dir + output_filename,
                    # options,
                ]
            )
            cr.run_bash_command(command)
    gc.collect()


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
    gc.collect()


def pochi_extract_birthmark(
    project_file, birthmark, software_location=BIRTHMARK_SOFTWARE
):
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


def run_pochi_pairs_dataframe_script_output(
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

        pochi_extract_compare_script_output(
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


def run_pochi_pairs_dataframe(
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


def run_pochi_similar_projects(output_option="no-csv", is_multiproc=False):
    similarity_groups = __get_similar_projects_pairs(
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
        __run_multiproc_script_output(project_pairs, output_option)
        return

    cm.init_csv_file(POCHI_OUTPUT_FILENAME, POCHI_OUTPUT_HEADER, OUTPUT_DIR)

    run_pochi_pairs_dataframe(pairs_dataframe=project_pairs, options=output_option)


def run_pochi_project_pair(
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

    pochi_extract_compare_script_output(
        project1=project1,
        project2=project2,
        project1_ver=project1_version,
        project2_ver=project2_version,
        project1_file_list=project1_file_list,
        project2_file_list=project2_file_list,
        output_filename=output_filename,
        options=options,
    )


def run_pochi_all(dir, output_option=None, is_multiproc=False, distinct_projects=True):
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
    pairs_df = __create_project_pairs(df, distinct_projects)

    if is_multiproc:
        __run_multiproc_script_output(pairs_df, output_option)
        result_df = __combine_temp_files()
        __drop_temp_files()
        result_df.to_csv(OUTPUT_DIR + POCHI_OUTPUT_FILENAME)
        return

    gc.collect()

    cm.init_csv_file(POCHI_OUTPUT_FILENAME, POCHI_OUTPUT_HEADER, OUTPUT_DIR)
    run_pochi_pairs_dataframe(pairs_dataframe=pairs_df, options=output_option)


def run_pochi_single_project_old(project_name, project_type):
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
    pairs_df = __create_project_pairs(df)

    output_filename = POCHI_VERSION + "_" + project_name + "_versions.csv"
    run_pochi_pairs_dataframe(pairs_dataframe=pairs_df, output_filename=output_filename)


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
    pairs_df = __create_project_pairs(df)

    output_filename = POCHI_VERSION + "_" + project_name + "_versions.csv"
    # cm.init_csv_file(output_filename, POCHI_OUTPUT_HEADER, OUTPUT_DIR)
    __drop_temp_files()
    run_pochi_pairs_dataframe(pairs_dataframe=pairs_df, output_filename=output_filename)
    result_df = __combine_temp_files()
    __drop_temp_files()
    result_df.to_csv(OUTPUT_DIR + output_filename)


def run_pochi_single_category_script_output(
    project_type, distinct_projects=True, is_multiproc=False
):
    project_files_data = []
    project_list = pi.get_project_list(TESTED_SOFTWARE_DIR, project_type)

    for project_name in project_list:
        project_versions = pi.get_project_version_list(
            TESTED_SOFTWARE_DIR, project_name, project_type
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
    pairs_df = __create_project_pairs(df, distinct_projects)

    project_type = project_type.replace("/", "")

    filename_suffix = ""

    match distinct_projects:
        case None:
            filename_suffix = "all"
        case True:
            filename_suffix = "distinct"
        case False:
            filename_suffix = "versions"

    output_filename = "_".join(
        [POCHI_VERSION, project_type, filename_suffix, "output.csv"]
    )

    if is_multiproc:
        #temp_folder = "F:/temp/"

        __drop_temp_files()
        __run_multiproc_script_output(pairs_df)
        #result_df = __combine_temp_files()
        #__drop_temp_files()
        #result_df.to_csv(OUTPUT_DIR + output_filename, index=False)
        return

    run_pochi_pairs_dataframe_script_output(pairs_df, output_filename=output_filename)


def run_pochi_single_category(project_type, distinct_projects=True, is_multiproc=False):
    project_files_data = []
    project_list = pi.get_project_list(TESTED_SOFTWARE_DIR, project_type)

    for project_name in project_list:
        project_versions = pi.get_project_version_list(
            TESTED_SOFTWARE_DIR, project_name, project_type
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
    pairs_df = __create_project_pairs(df, distinct_projects)

    project_type = project_type.replace("/", "")

    filename_suffix = ""

    match distinct_projects:
        case None:
            filename_suffix = "all"
        case True:
            filename_suffix = "distinct"
        case False:
            filename_suffix = "versions"

    output_filename = "_".join(
        [POCHI_VERSION, project_type, filename_suffix, "output.csv"]
    )

    if is_multiproc:
        __drop_temp_files()
        __run_multiproc(pairs_df)
        result_df = __combine_temp_files()
        __drop_temp_files()
        result_df.to_csv(OUTPUT_DIR + output_filename, index=False)
        return

    run_pochi_pairs_dataframe(pairs_df, output_filename=output_filename)


def run_pochi_for_each_category(distinct_projects=True):
    type_list = pi.get_project_types_list()
    for project_type in type_list:
        run_pochi_single_category(project_type, distinct_projects)


def run_pochi_category_pair(project_type1, project_type2, distinct_projects=True):
    project_files_data = []
    project_list1 = pi.get_project_list(TESTED_SOFTWARE_DIR, project_type1)
    project_list2 = pi.get_project_list(TESTED_SOFTWARE_DIR, project_type2)

    for project_name in project_list1:
        project_versions = pi.get_project_version_list(
            TESTED_SOFTWARE_DIR, project_name, project_type1
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
            TESTED_SOFTWARE_DIR, project_name, project_type2
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
    pairs_df = __create_project_pairs(df, distinct_projects)
    project_type1 = project_type1.replace("/", "")
    project_type2 = project_type2.replace("/", "")
    output_filename = "_".join(
        [POCHI_VERSION, project_type1, project_type2, "output.csv"]
    )

    run_pochi_pairs_dataframe(pairs_dataframe=pairs_df, output_filename=output_filename)
