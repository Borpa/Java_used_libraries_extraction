import pandas as pd
import os

BIRTHMARK_DATA_DIR = "./birthmarks/"
GROUPBY_OUTPUT_FILENAME = "groupby_info"
AVG_SIMILARITY_OUTPUT_FILENAME = "avg_similarity"
OUTPUT_DIR = "./birthmarks_group_data/"


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

    birthmark_files = os.listdir(BIRTHMARK_DATA_DIR)
    for file in birthmark_files:
        similarity_output_filename = file.replace(".csv", "") + "_avg_similarity"
        calculate_avg_similarity(file, similarity_output_filename)
        # count_output_filename = file.replace(".csv", "") + "_count"
        # calculate_groups_count(dataframe, count_output_filename)

    # retrieve_group_info(dataframe)


if __name__ == "__main__":
    main()
