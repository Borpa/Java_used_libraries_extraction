import itertools
from itertools import repeat
from multiprocessing import Pool, freeze_support

import numpy as np
from pandas import read_csv

import csv_manager as cm
from extract_files_external_deps import FILES_DEP
from extract_project_dependencies import DEP_DIR

FILES_SIM = "file_similarity.csv"


def calculate_similarity(file_group, file_df):
    result = list()

    for file_index in file_group:
        file1 = file_df.iloc[file_index]
        for index, row in file_df.iloc[file_index + 1 :].iterrows():
            file2 = row

            file1_project = file1.project
            file2_project = file2.project
            file1_project_ver = file1.project_ver
            file2_project_ver = file2.project_ver

            if (
                file1_project == file2_project
                and file1_project_ver == file2_project_ver
            ):
                continue

            file1_name = file1.filename
            file2_name = file2.filename

            file1_deps = file1.dependencies
            file1_deps = [
                i.replace("'", "").strip("][").split(", ") for i in file1_deps
            ]
            file1_deps = list(itertools.chain.from_iterable(file1_deps))

            file2_deps = file2.dependencies
            file2_deps = [
                i.replace("'", "").strip("][").split(", ") for i in file2_deps
            ]
            file2_deps = list(itertools.chain.from_iterable(file2_deps))

            same_deps = set(file1_deps) & set(file2_deps)

            deps_ratio1 = len(same_deps) / len(file1_deps) * 100
            deps_ratio2 = len(same_deps) / len(file2_deps) * 100
            # Note: might change to just the amount of similar dependencies to reduce the effect of the files with low general amount of imports

            ratio = max([deps_ratio1, deps_ratio2])

            file1_type = file1.type
            file2_type = file2.type

            file1_path = file1.filepath
            file2_path = file2.filepath

            result.append(
                [
                    file1_name,
                    file2_name,
                    file1_type,
                    file2_type,
                    ratio,
                    file1_project,
                    file2_project,
                    file1_project_ver,
                    file2_project_ver,
                    file1_path,
                    file2_path,
                ]
            )

    return result


def main():
    csv_data = read_csv(DEP_DIR + FILES_DEP)

    num_of_files = len(csv_data)

    file_groups_nums = [i for i in range(0, num_of_files)]
    file_groups_nums = np.array_split(file_groups_nums, 3)

    with Pool() as pool:
        result = pool.starmap(
            calculate_similarity, zip(file_groups_nums, repeat(csv_data))
        )

    header = [
        "filename1",
        "filename2",
        "project1_type",
        "project2_type",
        "dependency_ratio",
        "project1",
        "project2",
        "project1_ver",
        "project2_ver",
        "filepath1",
        "filepath2",
    ]

    result = list(itertools.chain.from_iterable(result))

    cm.init_csv_file(FILES_SIM, header, DEP_DIR)
    cm.append_csv_data(FILES_SIM, result, DEP_DIR)


if __name__ == "__main__":
    freeze_support()
    main()
