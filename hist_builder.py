import os
import pandas as pd


def hist_builder(
    birthmark_file, groupby_columns_val, output_dir, chunk_size=1e6, bins=25
):
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

    output_dir = output_dir + "histograms/" + filename + "/"

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
