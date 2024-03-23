from run_pochi import (
    check_classfile_local,
    check_classfile_size,
    check_classfile_only_size,
)
import pandas as pd
import os
import re
from extract_project_dependencies import TESTED_SOFTWARE_DIR
import time

# TEST_PROJ_DIR = TESTED_SOFTWARE_DIR
TEST_PROJ_DIR = "D:/Study/phd_research/test_projects/"


def get_project_type(filename):
    result = re.search("^(pochi-2.6.0)_(\w+)_(distinct|versions)", filename)
    return result.group(2)


def get_file_fullpath(project, project_type, project_ver, project_file):
    project_dir = "/".join([project_type, project, project_ver])
    project_dir = TEST_PROJ_DIR + project_dir

    for root, dirs, files in os.walk(project_dir):
        for file in files:
            if file == project_file:
                return os.path.join(root, file).replace("\\", "/")


def check_class(line, project_type):
    project1_file = get_file_fullpath(
        line.project1, project_type, line.project1_ver, line.project1_file
    )
    project2_file = get_file_fullpath(
        line.project2, project_type, line.project2_ver, line.project2_file
    )
    class1 = line.class1
    class2 = line.class2

    check1 = check_classfile_local(project1_file, class1) is not False
    check2 = check_classfile_local(project2_file, class2) is not False

    return check1 and check2


def check_class_single(project, project_ver, project_file, project_class, project_type):
    project_file_path = get_file_fullpath(
        project, project_type, project_ver, project_file
    )

    return check_classfile_local(project_file_path, project_class)


def check_class_size_single(
    project, project_ver, project_file, project_class, project_type
):
    project_file_path = get_file_fullpath(
        project, project_type, project_ver, project_file
    )
    return check_classfile_only_size(project_file_path, project_class)


def main():
    chunksize = 1000000
    birthmark_dir = "G:/Study/phd_research/birthmarks/"
    output_dir = "filtered/"

    birthmark_files = os.listdir(birthmark_dir)
    for birthmark_file in birthmark_files:
        if not birthmark_file.endswith(".csv"):
            continue
        # birthmark_file = "pochi-2.6.0_calculator_versions_output.csv"
        header_check = True
        with open(
            birthmark_dir
            + output_dir
            + birthmark_file.replace("_output", "_output_filtered"),
            "a",
            newline="",
        ) as file:
            project_type = get_project_type(birthmark_file)
            for chunk in pd.read_csv(
                birthmark_dir + birthmark_file, chunksize=chunksize
            ):
                # mask = chunk.apply(
                #    lambda x: check_class(x, project_type),
                #    axis=1,
                # )
                # chunk = chunk[mask]

                i = 0
                max_i = len(chunk)
                while i < max_i:
                    cur_row = chunk.iloc[i]
                    check1 = check_class_single(
                        cur_row.project1,
                        cur_row.project1_ver,
                        cur_row.project1_file,
                        cur_row.class1,
                        project_type,
                    )
                    if not check1:
                        chunk = chunk[chunk.class1 != cur_row.class1]
                        max_i = len(chunk)
                        continue

                    check2 = check_class_single(
                        cur_row.project2,
                        cur_row.project2_ver,
                        cur_row.project2_file,
                        cur_row.class2,
                        project_type,
                    )
                    if not check2:
                        chunk = chunk[chunk.class2 != cur_row.class2]
                        max_i = len(chunk)
                        continue
                    i += 1

                chunk.to_csv(file, index=False, header=header_check)
                header_check = False


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(end - start)
