import pandas as pd
import os

import project_inspector as pi
from run_pochi import POCHI_OUTPUT_HEADER

BIRTHMARK_DATA_DIR = "./birthmarks/"
GROUPBY_OUTPUT_FILENAME = "groupby_info"
AVG_SIMILARITY_OUTPUT_FILENAME = "avg_similarity"
OUTPUT_DIR = "./birthmarks_group_data/"


def full_column_names_check(file):
    chunksize = 1000000
    for chunk in pd.read_csv(file, chunksize=chunksize):
        return "project1" in chunk.columns.to_list()


def update_columns(file):
    chunksize = 100000
    output_filename = file.replace(".csv", "_new_header.csv")

    #with open(output_filename, "w") as f:
    #    f.write(",".join(POCHI_OUTPUT_HEADER) + "\n")

    with open(output_filename, "a") as f:
        for chunk in pd.read_csv(file, chunksize=chunksize):
            chunk = chunk[chunk.file1 != "file1"]

            chunk["project1"] = chunk.apply(
                lambda x: pi.get_project_name(x["file1"]), axis=1
            )
            chunk["project2"] = chunk.apply(
                lambda x: pi.get_project_name(x["file2"]), axis=1
            )
            chunk["project1_ver"] = chunk.apply(
                lambda x: pi.get_project_ver(x["file1"], x["project1"]), axis=1
            )
            chunk["project2_ver"] = chunk.apply(
                lambda x: pi.get_project_ver(x["file2"], x["project2"]), axis=1
            )
            chunk["project1_file"] = chunk.apply(
                lambda x: os.path.basename(x["file1"]), axis=1
            )
            chunk["project2_file"] = chunk.apply(
                lambda x: os.path.basename(x["file2"]), axis=1
            )
            chunk["birthmark"] = chunk["currentBirthmark"]
            chunk["comparator"] = chunk["currentComparator"]
            chunk["matcher"] = chunk["currentMatcher"]
            chunk["class1"] = chunk["class1"]
            chunk["class2"] = chunk["class2"]
            chunk["similarity"] = chunk["similarity"]

            chunk = chunk.drop(
                [
                    "file1",
                    "file2",
                    "currentBirthmark",
                    "currentMatcher",
                    "currentComparator",
                ],
                axis=1,
            )

            chunk.to_csv(f, index=False)


def retrieve_group_info(dataframe, output_filename=GROUPBY_OUTPUT_FILENAME):
    dataframe = dataframe.loc[dataframe.similarity == 1]
    dataframe = dataframe[
        [
            "project1",
            "project1_ver",
            "project2",
            "project2_ver",
            "project1_file",
            "project2_file",
            "birthmark",
            "comparator",
            "matcher",
            "class1",
            "class2",
        ]
    ]

    groupby_info = dataframe.groupby(["class1", "class2"]).size()

    with open(OUTPUT_DIR + output_filename, mode="w") as f:
        f.write(groupby_info.to_string())


def calculate_avg_similarity(file, output_filename=AVG_SIMILARITY_OUTPUT_FILENAME):
    column_list = [
        "project1",
        "project1_ver",
        "project2",
        "project2_ver",
        "birthmark",
        "comparator",
        "matcher",
        "similarity",
    ]

    dataframe = pd.read_csv(file)[column_list]
    column_list.remove("similarity")

    avg_values = dataframe.groupby([*column_list]).mean("similarity")
    count_values = (
        dataframe.groupby([*column_list])["similarity"]
        .count()
        .reset_index(name="count")
    )

    result = pd.merge(avg_values, count_values, on=[*column_list])
    result.to_csv(OUTPUT_DIR + output_filename + ".csv")

    # with open(OUTPUT_DIR + output_filename, mode="w") as f:
    #    f.write(result.to_string())


def calculate_groups_count(dataframe, output_filename):
    column_list = [
        "project1",
        "project1_ver",
        "project2",
        "project2_ver",
        "birthmark",
        "comparator",
        "matcher",
        "similarity",
    ]

    dataframe = dataframe[column_list]
    column_list.remove("similarity")

    count_values = dataframe.groupby([*column_list]).count().reset_index(name="count")
    with open(OUTPUT_DIR + output_filename, mode="w") as f:
        f.write(count_values.to_string())


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    else:
        for file in os.listdir(OUTPUT_DIR):
            os.remove(OUTPUT_DIR + file)

    birthmark_dir = "G:/Study/phd_research/birthmarks/"

    birthmark_files = os.listdir(birthmark_dir)
    for file in birthmark_files:
        if not file.endswith(".csv"):
            continue

        similarity_output_filename = file.replace(".csv", "") + "_avg_similarity"
        calculate_avg_similarity(file, similarity_output_filename)
        # count_output_filename = file.replace(".csv", "") + "_count"
        # calculate_groups_count(dataframe, count_output_filename)

    # retrieve_group_info(dataframe)


if __name__ == "__main__":
    main()
