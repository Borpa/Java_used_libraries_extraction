import csv
import itertools
from itertools import repeat
from multiprocessing import Pool, freeze_support

import numpy as np
from pandas import read_csv

dependency_data = "files_dependencies.csv"
similarity_output_filename = "file_similarity.csv"


def calculate_similarity(file_group, file_df):
    result = list()

    for file_index in file_group:
        file1 = file_df.iloc[file_index]
        for index, row in file_df.iloc[file_index + 1 :].iterrows():
            file2 = row

            file1_project = file1.project
            file2_project = file2.project

            if file1_project == file2_project:
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
                    file1_path,
                    file2_path,
                ]
            )

    return result


def main():
    csv_data = read_csv(dependency_data)

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
        "filepath1",
        "filepath2",
    ]

    result = list(itertools.chain.from_iterable(result))

    with open(similarity_output_filename, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for res in result:
            writer.writerow(res)


if __name__ == "__main__":
    freeze_support()
    main()
