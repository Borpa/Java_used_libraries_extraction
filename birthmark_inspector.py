import pandas as pd
import os

import project_inspector as pi
from run_pochi import POCHI_OUTPUT_HEADER

BIRTHMARK_DATA_DIR = "./birthmarks/"
GROUPBY_OUTPUT_FILENAME = "groupby_info"
AVG_SIMILARITY_OUTPUT_FILENAME = "avg_similarity"
OUTPUT_DIR = "./birthmarks_group_data/"
OUTPUT_DIR_FULL = "D:/Study/phd_research/library_extraction/birthmarks_group_data/"


def full_column_names_check(file):
    chunksize = 1e6
    for chunk in pd.read_csv(file, chunksize=chunksize):
        return "project1" in chunk.columns.to_list()


def filter_multiple_headers(birthmark_file):
    chunksize = 1e6
    header_check = True
    for chunk in pd.read_csv(birthmark_file, chunksize=chunksize):
        chunk = chunk[chunk.project1 != "project1"]
        with open(
            birthmark_file.replace(".csv", "_new.csv"),
            "a",
            newline="",
        ) as file:
            chunk.to_csv(file, index=False, header=header_check)
            header_check = False


def add_header(filename, new_filename):
    with open(new_filename, "a", newline="") as file:
        file.write(",".join(POCHI_OUTPUT_HEADER))
        file.write("\n")
        for chunk in pd.read_csv(filename, chunksize=1e6):
            chunk = chunk[chunk.iloc[:, 0] != "project1"]
            chunk.to_csv(file, header=False, index=False)


def update_columns(file):
    chunksize = 1e6
    output_filename = file.replace(".csv", "_new_header.csv")

    # with open(output_filename, "w") as f:
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


def calculate_avg_similarity(
    file, output_filename=AVG_SIMILARITY_OUTPUT_FILENAME, threshold=None
):
    column_list = [
        "project1",
        "project1_ver",
        "project2",
        "project2_ver",
        "birthmark",
        "comparator",
        "matcher",
    ]
    chunksize = 1e6
    column_list_full = column_list + ["similarity"]

    header_check = True

    for chunk in pd.read_csv(file, chunksize=chunksize):
        if threshold is not None:
            chunk = chunk[chunk.similarity >= threshold]
        chunk = chunk[chunk.project1 != "project1"]
        chunk = chunk[column_list_full]
        avg_values = chunk.groupby([*column_list]).mean("similarity")
        count_values = (
            chunk.groupby([*column_list])["similarity"]
            .count()
            .reset_index(name="count")
        )
        result = pd.merge(avg_values, count_values, on=[*column_list])

        with open(OUTPUT_DIR + output_filename, "a", newline="") as f:
            result.to_csv(f, index=False, header=header_check)

        header_check = False

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


def combine_groups_files(
    group1_dir="./birthmarks_group_data/",
    group2_dir="w_threshold/",
    similarity_col="similarity_w_threshold",
    count_col="count_w_threshold",
):
    for file in os.listdir(group1_dir):
        if not file.endswith(".csv"):
            continue
        combined_file = (
            file.replace("_groupby.csv", "") + "_filtered_avg_similarity.csv"
        )
        df1 = pd.read_csv(group1_dir + file)
        df2 = pd.read_csv(group1_dir + group2_dir + combined_file)
        df2 = df2.rename(
            columns={
                "similarity": similarity_col,
                "count": count_col,
            }
        )
        df3 = pd.merge(
            df1,
            df2,
            how="outer",
            on=[
                "project1",
                "project1_ver",
                "project2",
                "project2_ver",
                "birthmark",
                "comparator",
                "matcher",
            ],
        )
        df3.similarity_filtered = df3.similarity_filtered.fillna(0)
        df3.count_filtered = df3.count_filtered.fillna(0)
        df3.count_filtered = df3.count_filtered.astype(int)

        df3.similarity_w_threshold = df3.similarity_w_threshold.fillna(0)
        df3.count_w_threshold = df3.count_w_threshold.fillna(0)
        df3.count_w_threshold = df3.count_w_threshold.astype(int)
        df3.to_csv(group1_dir + "combined/" + file, index=False)


def merge_duplicates(group_data_dir="./birthmarks_group_data/w_threshold/"):
    for group_file in os.listdir(group_data_dir):
        if not group_file.endswith(".csv"):
            continue
        df = pd.read_csv(group_data_dir + group_file)
        groupby_cols = [
            "project1",
            "project1_ver",
            "project2",
            "project2_ver",
            "birthmark",
            "comparator",
            "matcher",
        ]
        df = df.groupby([*groupby_cols], as_index=False).agg(
            {"similarity": "mean", "count": "sum"}
        )
        df.to_csv(group_data_dir + group_file, index=False)


def hist_builder(birthmark_file, groupby_columns_val, chunk_size=1e6):
    project1 = groupby_columns_val[0]
    project1_ver = groupby_columns_val[1]
    project2 = groupby_columns_val[2]
    project2_ver = groupby_columns_val[3]
    birthmark = groupby_columns_val[4]
    comparator = groupby_columns_val[5]
    matcher = groupby_columns_val[6]

    groupby_cols = [
        "project1",
        "project1_ver",
        "project2",
        "project2_ver",
        "birthmark",
        "comparator",
        "matcher",
    ]

    chunks = pd.read_csv(birthmark_file, chunksize=chunk_size)

    result_df = pd.DataFrame()

    for chunk in chunks:
        chunk_group_vals = chunk[
            (chunk.project1 == project1)
            & (chunk.project1_ver == project1_ver)
            & (chunk.project2 == project2)
            & (chunk.project2_ver == project2_ver)
            & (chunk.birthmark == birthmark)
            & (chunk.comparator == comparator)
            & (chunk.matcher == matcher)
        ]
        result_df = pd.concat([result_df, chunk_group_vals])

    result_df = result_df.drop(
        columns=["class1", "class2", "project1_file", "project2_file"]
    )
    result_df["similarity"].hist(
        bins=20, range=(0, 1), color="blue", ec="blue"
    ).get_figure().savefig(
        OUTPUT_DIR + "histograms/" + "_".join(groupby_columns_val) + ".jpeg"
    )


def plot_histograms(birthmark_dir):
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        groupby_cols = [
            "project1",
            "project1_ver",
            "project2",
            "project2_ver",
            "birthmark",
            "comparator",
            "matcher",
        ]

        columns_set = None

        for chunk in pd.read_csv(birthmark_dir + birthmark_file, chunksize=1e6):
            groupby = chunk.groupby([*groupby_cols])
            columns_set = groupby.groups

        for column_set in columns_set:
            hist_builder(birthmark_dir + birthmark_file, column_set)


def main():
    # if not os.path.exists(OUTPUT_DIR):
    #    os.makedirs(OUTPUT_DIR)
    # else:
    #    for file in os.listdir(OUTPUT_DIR):
    #        os.remove(OUTPUT_DIR + file)

    #birthmark_dir = "G:/Study/phd_research/birthmarks/test/"
    #plot_histograms(birthmark_dir)

    birthmark_group_dir = (
       "D:/Study/phd_research/library_extraction/birthmarks_group_data/"
    )
    group2 = "filtered/combined/"

    # birthmark_files = os.listdir(birthmark_dir)
    # for file in birthmark_files:
    #    if not file.endswith(".csv"):
    #        continue
    #    similarity_output_filename = file.replace(".csv", "") + "_groupby.csv"
    #    calculate_avg_similarity(birthmark_dir + file, similarity_output_filename)

    # merge_duplicates(birthmark_group_dir)

    combine_groups_files(
       birthmark_group_dir, group2, "similarity_filtered", "count_filtered"
    )

    # count_output_filename = file.replace(".csv", "") + "_count"
    # calculate_groups_count(dataframe, count_output_filename)

    # retrieve_group_info(dataframe)


if __name__ == "__main__":
    main()
