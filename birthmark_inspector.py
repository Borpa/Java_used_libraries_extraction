import pandas as pd
import os

import project_inspector as pi
from run_pochi import POCHI_OUTPUT_HEADER, POCHI_OUTPUT_HEADER_AVG

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
    file,
    output_filename=AVG_SIMILARITY_OUTPUT_FILENAME,
    threshold=None,
    output_dir=OUTPUT_DIR,
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
        if chunk.columns[0] != "project1":
            # chunk.columns = POCHI_OUTPUT_HEADER
            chunk.columns = POCHI_OUTPUT_HEADER_AVG
            # chunk.columns = [
            #    "project1",
            #    "project2",
            #    "birthmark",
            #    "comparator",
            #    "similarity",
            # ]

        if threshold is not None:
            chunk = chunk[chunk.similarity >= threshold]
        chunk = chunk[chunk.project1 != "project1"]
        chunk = chunk[column_list_full]
        # result = chunk.groupby([*column_list]).mean("similarity")
        result = chunk.groupby([*column_list]).agg({"similarity": "mean"}).reset_index()
        # count_values = (
        #    chunk.groupby([*column_list])["similarity"]
        #    .count()
        #    .reset_index(name="count")
        # )
        # result = pd.merge(avg_values, count_values, on=[*column_list])

        with open(output_dir + output_filename, "a", newline="") as f:
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
        # df = df.groupby([*groupby_cols], as_index=False).agg(
        #    {"similarity": "mean", "count": "sum"}
        # )

        df = df.groupby([*groupby_cols]).agg({"similarity": "mean"}).reset_index()

        df.to_csv(group_data_dir + group_file, index=False)


def hist_builder(birthmark_file, groupby_columns_val, chunk_size=1e6, bins=25):
    # project1 = groupby_columns_val[0]
    # project1_ver = groupby_columns_val[1]
    # project2 = groupby_columns_val[2]
    # project2_ver = groupby_columns_val[3]
    filename = os.path.basename(birthmark_file)

    birthmark = groupby_columns_val[0]
    comparator = groupby_columns_val[1]
    matcher = groupby_columns_val[2]

    chunks = pd.read_csv(birthmark_file, chunksize=chunk_size)

    result_df = pd.DataFrame()

    for chunk in chunks:
        chunk_group_vals = chunk[
            # (chunk.project1 == project1)
            # & (chunk.project1_ver == project1_ver)
            # & (chunk.project2 == project2)
            # & (chunk.project2_ver == project2_ver)
            (chunk.birthmark == birthmark)
            & (chunk.comparator == comparator)
            & (chunk.matcher == matcher)
        ]
        result_df = pd.concat([result_df, chunk_group_vals])

    result_df = result_df.drop(
        columns=["class1", "class2", "project1_file", "project2_file"]
    )

    output_dir = OUTPUT_DIR + "histograms/" + filename + "/"

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    result_df["similarity"].hist(
        bins=bins, range=(0, 1), color="blue", ec="blue"
    ).get_figure().savefig(output_dir + "_".join(groupby_columns_val) + ".jpeg")


def plot_histograms(birthmark_dir):
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        groupby_cols = [
            # "project1",
            # "project1_ver",
            # "project2",
            # "project2_ver",
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


def separate_into_dirs(birthmark_dir, project_category, main_dir):
    files = os.listdir(birthmark_dir)
    birthmarks = ["3-gram", "6-gram", "uc", "fuc"]
    sim_func = ["Cosine", "DiceIndex", "JacardCoefficient", "SimpsonIndex"]

    for file in files:
        if not file.endswith(".csv"):
            continue
        if project_category not in file:
            continue

        df = pd.read_csv(birthmark_dir + file)
        df_groups = df.groupby(["birthmark", "comparator"], as_index=False)

        for group in df_groups:
            output_dir = main_dir
            output_dir = output_dir + "_".join(
                [project_category, group[0][0], group[0][1] + "/"]
            )

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            if "distinct" in file:
                output_filename = project_category + "_distinct.csv"
            else:
                output_filename = project_category + "_versions.csv"

            with open(output_dir + output_filename, "a", newline="") as f:
                group[1].to_csv(f, index=False)


def class_filter(birthmark_dir, author_list, output_dir="filtered/"):
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        df = pd.read_csv(birthmark_dir + birthmark_file)

        res = None
        for author in author_list:
            df1 = df[df.class1.str.contains(author)]
            df2 = df[df.class2.str.contains(author)]

            res = pd.concat([res, df1, df2])
        res = res[res.duplicated(keep=False)].drop_duplicates()

        res.to_csv(birthmark_dir + output_dir + birthmark_file, index=False)


def filter_by_top_N(birthmark_dir, N, output_dir="top3/"):
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        df = pd.read_csv(birthmark_dir + birthmark_file)
        groupby_cols = [
            "project1",
            "project2",
            "project1_ver",
            "project2_ver",
            "birthmark",
            "comparator",
            "matcher",
        ]
        df = df.groupby([*groupby_cols])["similarity"].nlargest(N).reset_index()
        header = [
            "project1",
            "project2",
            "project1_ver",
            "project2_ver",
            "birthmark",
            "comparator",
            "matcher",
            "similarity",
        ]
        df = df[header]

        df.to_csv(birthmark_dir + output_dir + birthmark_file, index=False)


def get_group_avg_sim(birthmark_dir, output_dir="avg/"):
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        df = pd.read_csv(birthmark_dir + birthmark_file)

        gb = (
            df.groupby(
                [
                    "project1",
                    "project2",
                    "project1_ver",
                    "project2_ver",
                    "birthmark",
                    "comparator",
                    "matcher",
                ]
            )
            .agg({"similarity": "mean"})
            .reset_index()
        )

        gb.to_csv(birthmark_dir + output_dir + birthmark_file, index=False)


def main():
    bmdir = "D:/Study/phd_research/library_extraction/birthmarks/topsim_classes/filtered/top3/"

    get_group_avg_sim(bmdir)
    #class_filter(bmdir, author_list)
    #filter_by_top_N(bmdir, 3)


if __name__ == "__main__":
    main()
