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
from custom_similarity_functions import compare_all


BIRTHMARK_SOFTWARE = (
    "C:/Users/FedorovNikolay/source/Study/birthmark_extraction_software/"
)
# BIRTHMARK_SOFTWARE = "D:/Study/phd_research/birthmark_extraction_software/"

SIMILARITY_THRESHOLD = 70
SIMILARITY_PAIRS_NUM = 3

POCHI_VERSION = "pochi-2.6.0"
POCHI_OUTPUT_FILENAME = POCHI_VERSION + "_output_w_ver.csv"
OUTPUT_DIR = "./birthmarks/"

NUM_OF_PROC = 2
MULTIPROC_TEMP_DIR = "./temp/"
MULTIPROC_TEMP_DIR_SHORT = "./temp/"
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

POCHI_OUTPUT_HEADER_ALT = [
    "project1",
    "project2",
    "project1_ver",
    "project2_ver",
    "birthmark",
    "comparator",
    "matcher",
    "class1",
    "class2",
    "similarity",
]


POCHI_OUTPUT_HEADER_ALT_2 = [
    "project1_file",
    "project2_file",
    "birthmark",
    "comparator",
    "matcher",
    "class1",
    "class2",
    "similarity",
]


POCHI_OUTPUT_HEADER_AVG = [
    "project1",
    "project1_ver",
    "project2",
    "project2_ver",
    "birthmark",
    "comparator",
    "matcher",
    "similarity",
]

POCHI_OUTPUT_HEADER_MAX_SIM = [
    "project1",
    "project2",
    "project1_ver",
    "project2_ver",
    "birthmark",
    "comparator",
    "matcher",
    #"class1",
    #"class2",
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


def combine_temp_files(temp_dir=MULTIPROC_TEMP_DIR):
    temp_files = os.listdir(temp_dir)
    df_list = []

    for temp_file in temp_files:
        df = pd.read_csv(temp_dir + temp_file)
        df_list.append(df)
    return pd.concat(df_list)


def combine_temp_files_alt(
    temp_dir=MULTIPROC_TEMP_DIR,
    output_filename="pochi.csv",
    output_dir=MULTIPROC_TEMP_DIR,
):
    temp_files = os.listdir(temp_dir)
    chunksize = 1e6
    header_check = True

    for temp_file in temp_files:
        with open(output_dir + output_filename, "a", newline="") as f:
            for chunk in pd.read_csv(temp_dir + temp_file, chunksize=chunksize):
                chunk.to_csv(f, index=False, header=header_check)
                header_check = False


def __drop_temp_files(temp_dir=MULTIPROC_TEMP_DIR):
    temp_files = os.listdir(temp_dir)
    for temp_file in temp_files:
        os.remove(temp_dir + temp_file)


def __multiproc_run_iteration_script_output(proj_pair_group, output_option):
    pid = current_process().pid
    temp_file_name = str(pid) + ".csv"
    cm.init_csv_file(temp_file_name, POCHI_OUTPUT_HEADER_ALT_2, MULTIPROC_TEMP_DIR)

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
    proj_pair_groups = np.array_split(project_pairs, NUM_OF_PROC)

    with Pool() as pool:
        pool.starmap(
            __multiproc_run_iteration_script_output,
            zip(proj_pair_groups, repeat(output_option)),
        )


def __run_multiproc(project_pairs, output_option=None):
    proj_pair_groups = np.array_split(project_pairs, NUM_OF_PROC)

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


def check_classfile_local_simple(project_name, classfile):
    author, project = project_name.lower().split("_")
    classfile_dirs = classfile.lower().split(".")

    return (
        (author in classfile_dirs)
        or (project in classfile_dirs)
        or (project.replace("-", "") in classfile_dirs)
        or (project.split("-")[0] in classfile_dirs)
    )


def check_classfile_local(project_file, classfile):  # check if local dep
    # pochi output for file sctruct: <path>$<classname>
    classfile = classfile.split("$")[0]
    src_dir = pi.get_src_dir(project_file)
    classpath = classfile.replace(".", "/")
    if src_dir is None:
        return False
    src_dir_alt = src_dir + "/main/java"

    fullpath = src_dir + "/" + classpath + ".java"
    if os.path.isfile(fullpath):
        return os.path.isfile(fullpath)

    fullpath = src_dir_alt + "/" + classpath + ".java"
    return os.path.isfile(fullpath)


def check_classfile_size(project_file, classfile):  # check if local dep + size
    # pochi output for file sctruct: <path>$<classname>
    classfile = classfile.split("$")[0]
    src_dir = pi.get_src_dir(project_file)
    classpath = classfile.replace(".", "/")
    if src_dir is None:
        return False
    fullpath = src_dir + "/" + classpath + ".java"
    fullpath_alt = src_dir + "/main/java" + classpath + ".java"

    for filepath in [fullpath, fullpath_alt]:
        if os.path.isfile(filepath):
            filesize = os.path.getsize(filepath)
            return filesize > (3 * 1024)  # ignore file if filesize is under 3 KB

    return False


def check_classfile_only_size(project_file, classfile):  # for filtered results
    classfile = classfile.split("$")[0]
    src_dir = pi.get_src_dir(project_file)
    classpath = classfile.replace(".", "/")
    fullpath = src_dir + "/" + classpath + ".java"
    # TODO: add additional check for java/main/ path
    try:
        filesize = os.path.getsize(fullpath)
    except FileNotFoundError:
        fullpath = src_dir + "/main/java/" + classpath + ".java"
        filesize = os.path.getsize(fullpath)

    return filesize > (3 * 1024)


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
    extraction_script = "./pochi_scripts/" + "extract-compare_w_output.groovy"

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
            cr.run_bash_command_file_output(command, output_dir + output_filename, "a")
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

            # file_pair_result = []

            for line in cr.run_bash_command(command).split("\r\n"):
                if len(line) == 0:
                    continue
                line = line.replace("\r\n", "").split(",")
                # class1 = line[3]
                # class2 = line[4]
                # check1 = check_classfile_local(project1_file, class1)
                # check2 = check_classfile_local(project2_file, class2)

                # if not (check1 and check2):
                #    continue

                newline = [
                    project1,
                    project2,
                    project1_ver,
                    project2_ver,
                    os.path.basename(project1_file),
                    os.path.basename(project2_file),
                ] + line
                # file_pair_result.append(newline)
                cm.append_single_entry(output_filename, newline, output_dir)

            # cm.append_csv_data(output_filename, file_pair_result, output_dir)
    gc.collect()


def calculate_avg_similarity(
    project1,
    project2,
    project1_ver,
    project2_ver,
    sim_data,
    output_filename,
    output_dir=OUTPUT_DIR,
):
    if len(sim_data) == 0:
        return

    column_list = [
        "birthmark",
        "comparator",
        "matcher",
    ]
    column_list_full = column_list + ["similarity"]

    df = pd.DataFrame(sim_data)
    df.columns = column_list_full

    df = df[df.similarity != "NaN"]
    df["similarity"] = pd.to_numeric(df["similarity"])
    df = df[df.similarity >= 0.25]

    # result = df.groupby([*column_list]).mean("similarity")
    result = df.groupby([*column_list]).agg({"similarity": "mean"}).reset_index()

    if len(result) == 0:
        return

    result[["project1", "project1_ver", "project2", "project2_ver"]] = [
        [project1, project1_ver, project2, project2_ver] for i in range(len(result))
    ]
    result = result[POCHI_OUTPUT_HEADER_AVG]

    # df = pd.merge(df.groupby([*column_list]), result, on=[*column_list])

    with open(output_dir + output_filename, "a", newline="") as file:
        result.to_csv(file, index=False, header=False)


def pochi_extract_compare_avg(
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
                ]
            )
            file_pair_result = []
            script_output = cr.run_bash_command(command).split("\r\n")
            line = script_output.pop()
            #for line in script_output:
            while script_output:
                if len(line) == 0:
                    line = script_output.pop()
                    continue
                newline = line.replace("\r\n", "").split(",")
                newline = newline[:3] + newline[5:]
                file_pair_result.append(newline)
                line = script_output.pop()
                #script_output.remove(line)
            #script_output = None
            calculate_avg_similarity(
                project1,
                project2,
                project1_ver,
                project2_ver,
                file_pair_result,
                output_filename,
                output_dir,
            )
            gc.collect()


def group_by_max_sim(
    project1,
    project2,
    project1_ver,
    project2_ver,
    sim_data,
    output_filename,
    output_dir=OUTPUT_DIR,
):
    #if len(sim_data) == 0:
    #    return

    column_list_min = [
        "birthmark",
        "comparator",
        "matcher",
    ]
    
    column_list_full = [
        "birthmark",
        "comparator",
        "matcher",
        "class1",
        "class2",
        "similarity",
    ]

    result = None
    groupby_columns1 = column_list_min + ["class1"]
    groupby_columns2 = column_list_min + ["class2"]

    if os.stat(sim_data).st_size == 0:
        return

    for chunk in pd.read_csv(sim_data, chunksize=1e7):
        chunk.columns = column_list_full
        #chunk = chunk[chunk.similarity != "NaN"]
        chunk['similarity'] = pd.to_numeric(chunk['similarity'], errors='coerce', downcast='float')
        #chunk["similarity"] = chunk["similarity"].apply(pd.to_numeric, downcast='float', errors='coerce')
        chunk = chunk.convert_dtypes()
        chunk["class1"] = chunk["class1"].str.split('$').str[0]
        chunk["class2"] = chunk["class2"].str.split('$').str[0]
    
        result1 = chunk.loc[chunk.groupby([*groupby_columns1])["similarity"].idxmax().dropna()]
        result2 = chunk.loc[chunk.groupby([*groupby_columns2])["similarity"].idxmax().dropna()]

        result = pd.concat([result, result1, result2]).drop_duplicates()

    result = result.groupby([*column_list_min]).agg({"similarity": "mean"}).reset_index()
    if len(result) == 0:
        return

    result[["project1", "project1_ver", "project2", "project2_ver"]] = [
        [project1, project1_ver, project2, project2_ver] for i in range(len(result))
    ]
    result = result[POCHI_OUTPUT_HEADER_MAX_SIM]

    with open(output_dir + output_filename, "a", newline="") as file:
        result.to_csv(file, index=False, header=False)


def pochi_extract_compare_max_sim(
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
    pochi_script = full_path + "pochi_unbuf"
    extraction_script = "./pochi_scripts/" + "extract-compare.groovy"

    for project1_file in project1_file_list:
        for project2_file in project2_file_list:
            command = " ".join(
                [
                    "sh",
                    pochi_script,
                    extraction_script,
                    project1_file,
                    project2_file,
                    #"> ./temp/temp.txt"
                ]
            )
            #file_pair_result = []
            
            script_output = cr.run_bash_command(command) #.split("\r\n")
            
            #line = script_output.pop()
            #while script_output:
            #    if len(line) == 0:
            #        line = script_output.pop()
            #        continue
            #    newline = line.replace("\r\n", "").split(",")

            #    file_pair_result.append(newline)
            #    line = script_output.pop()

            script_result = "./temp/temp.csv"
            group_by_max_sim(
                project1,
                project2,
                project1_ver,
                project2_ver,
                script_result,
                output_filename,
                output_dir,
            )
            gc.collect()


def pochi_extract_birthmark(
    project_file, birthmark, software_location=BIRTHMARK_SOFTWARE
):
    full_path = software_location + POCHI_VERSION + "/bin/"
    pochi_script = "sh " + full_path + "pochi"
    extraction_script = "./pochi_scripts/" + "extract_birthmark.groovy"
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
    cm.init_csv_file(output_filename, POCHI_OUTPUT_HEADER_MAX_SIM, output_dir)

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

        pochi_extract_compare_max_sim(
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
        result_df = combine_temp_files()
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
    cm.init_csv_file(output_filename, POCHI_OUTPUT_HEADER, OUTPUT_DIR)
    # __drop_temp_files()
    run_pochi_pairs_dataframe(pairs_dataframe=pairs_df, output_filename=output_filename)
    # result_df = combine_temp_files()
    # __drop_temp_files()
    # result_df.to_csv(OUTPUT_DIR + output_filename)


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
        # temp_folder = "F:/temp/"

        __drop_temp_files()
        __run_multiproc_script_output(pairs_df)
        combine_temp_files_alt(
            output_filename=output_filename,
            output_dir=OUTPUT_DIR,
        )
        # result_df = combine_temp_files()
        # __drop_temp_files()
        # result_df.to_csv(OUTPUT_DIR + output_filename, index=False)
        return

    run_pochi_pairs_dataframe_script_output(pairs_df, output_filename=output_filename)


def run_pochi_single_category_custom_list(
    project_type, project_list, distinct_projects=True, is_multiproc=False
):
    project_files_data = []

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
        [POCHI_VERSION, project_type, *project_list, filename_suffix, "output.csv"]
    )

    if is_multiproc:
        __drop_temp_files()
        __run_multiproc(pairs_df)
        combine_temp_files_alt(output_filename=output_filename, output_dir=OUTPUT_DIR)
        # result_df = combine_temp_files()
        # __drop_temp_files()
        # result_df.to_csv(OUTPUT_DIR + output_filename, index=False)
        return

    run_pochi_pairs_dataframe(pairs_df, output_filename=output_filename)


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
        combine_temp_files_alt(output_filename=output_filename, output_dir=OUTPUT_DIR)
        # result_df = combine_temp_files()
        # __drop_temp_files()
        # result_df.to_csv(OUTPUT_DIR + output_filename, index=False)
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


def extract_birthmarks(
    birthmark_list, project_type, combine=True, projects_dir=TESTED_SOFTWARE_DIR
):
    project_list = pi.get_project_list(projects_dir, project_type)
    output_dir_base = "./birthmarks/"

    for project_name in project_list:
        project_versions = pi.get_project_version_list(
            projects_dir, project_name, project_type
        )
        for project_ver in project_versions:
            project_file_list = pi.get_project_jar_list(
                projects_dir, project_type, project_name, project_ver
            )
            project_type = project_type.replace("/", "")

            for birthmark in birthmark_list:
                output_dir = (
                    output_dir_base
                    + "/".join([birthmark, project_type, project_name])
                    + "/"
                )
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                if combine:
                    output_filename = "_".join([project_name, project_ver, birthmark])
                #    with open(output_dir + output_filename, "a") as file:
                #        file.write(
                #            ",".join(
                #                [
                #                    "_".join([project_name, project_ver]),
                #                    "jar:file:///" + project_file_list[0],
                #                    birthmark,
                #                ]
                #            )
                #        )

                first_line_check = True

                for project_file in project_file_list:
                    extracted_birthmark = pochi_extract_birthmark(
                        project_file, birthmark
                    )

                    if combine:
                        with open(output_dir + output_filename, "a") as file:
                            for bm in extracted_birthmark:
                                if len(bm) == 0:
                                    continue
                                bm = bm.split(",")
                                bm_index = bm.index(birthmark)

                                if not first_line_check:
                                    file.write(",")
                                else:
                                    first_line_check = False

                                file.write(",".join(bm[bm_index + 1 :]))

                    else:
                        project_file_name = os.path.basename(project_file)
                        output_filename = "_".join([project_file_name, birthmark])
                        with open(output_dir + output_filename, "a") as file:
                            file.write("\n".join(extracted_birthmark))


def compare_external_birthmarks_pair_pochi(
    birthmark_file1,
    birthmark_file2,
    output_filename=None,
    output_dir=OUTPUT_DIR,
    software_location=BIRTHMARK_SOFTWARE,
):
    full_path = software_location + POCHI_VERSION + "/bin/"
    pochi_script = "sh " + full_path + "pochi"
    extraction_script = "./pochi_scripts/" + "compare_pair.groovy"

    command = " ".join(
        [
            pochi_script,
            extraction_script,
            birthmark_file1,
            birthmark_file2,
        ]
    )
    output = cr.run_bash_command(command)
    output = output.split("\r\n")

    birthmark_file1 = os.path.basename(birthmark_file1)
    birthmark_file2 = os.path.basename(birthmark_file2)

    return output


def compare_external_birthmarks_versions(
    project_types, birthmark_list, birthmark_dir="./birthmarks/external/"
):
    for current_birthmark in birthmark_list:
        for project_type in project_types:
            project_type = project_type.replace("/", "")

            projects_path = (
                birthmark_dir + "/".join([current_birthmark, project_type]) + "/"
            )

            project_dirs = os.listdir(projects_path)

            comparisons = []

            for project_dir in project_dirs:
                birthmark_files = os.listdir(projects_path + project_dir)
                birthmark_files = [
                    projects_path + project_dir + "/" + x for x in birthmark_files
                ]

                for i in range(0, len(birthmark_files)):
                    for j in range(i + 1, len(birthmark_files)):
                        if i == j:
                            continue
                        comparisons.append(
                            compare_all(
                                birthmark_files[i],
                                birthmark_files[j],
                                current_birthmark,
                            )
                        )

            with open(
                birthmark_dir + "_".join([project_type, "versions"]) + ".csv", "a"
            ) as file:
                for comparison in comparisons:
                    for line in comparison:
                        file.write(",".join(line) + "\n")


def compare_external_birthmarks_distinct(
    project_types, birthmark_list, birthmark_dir="./birthmarks/external/"
):
    for current_birthmark in birthmark_list:
        for project_type in project_types:
            project_type = project_type.replace("/", "")

            projects_path = (
                birthmark_dir + "/".join([current_birthmark, project_type]) + "/"
            )

            project_dirs = os.listdir(projects_path)

            comparisons = []

            project_birthmarks_groups = []

            for project_dir in project_dirs:
                project_group = os.listdir(projects_path + project_dir)
                project_birthmarks_groups.append(
                    [projects_path + project_dir + "/" + x for x in project_group]
                )

            for i in range(0, len(project_birthmarks_groups)):
                for j in range(i + 1, len(project_birthmarks_groups)):
                    if i == j:
                        continue

                    group1 = project_birthmarks_groups[i]
                    group2 = project_birthmarks_groups[j]

                    for birthmark1 in group1:
                        for birthmark2 in group2:
                            comparisons.append(
                                compare_all(birthmark1, birthmark2, current_birthmark)
                            )

            with open(
                birthmark_dir + "_".join([project_type, "distinct"]) + ".csv", "a"
            ) as file:
                for comparison in comparisons:
                    for line in comparison:
                        file.write(",".join(line) + "\n")
