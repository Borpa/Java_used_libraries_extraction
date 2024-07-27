import pandas as pd
import os

import project_inspector as pi
from run_pochi import POCHI_OUTPUT_HEADER, POCHI_OUTPUT_HEADER_AVG
from project_inspector import PROJECT_TYPES
from file_inspector import (
    Inspect_type,
    VALUE_COLUMN_SIZE,
    VALUE_COLUMN_LINE_COUNT,
    VALUE_COLUMN_INSTRUCT_COUNT,
)
from extra.authors import AUTHOR_LIST

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


def class_filter(birthmark_dir, author_list=AUTHOR_LIST, output_dir="filtered/"):
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        df = pd.read_csv(birthmark_dir + birthmark_file)

        authors_str = "|".join(author_list)

        res = df[
            (df.class1.str.contains(authors_str))
            & (df.class2.str.contains(authors_str))
        ]

        # res = None
        # for author in author_list:
        #    df1 = df[df.class1.str.contains(author)]
        #    df2 = df[df.class2.str.contains(author)]

        #    res = pd.concat([res, df1, df2])
        # res = res[res.duplicated(keep=False)].drop_duplicates()

        output_total = birthmark_dir + output_dir
        if not os.path.exists(output_total):
            os.makedirs(output_total)

        res.to_csv(output_total + birthmark_file, index=False)


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

        output_total = birthmark_dir + output_dir

        if not os.path.exists(output_total):
            os.makedirs(output_total)

        df.to_csv(output_total + birthmark_file, index=False)


def filter_by_top_perc(birthmark_dir, N_perc, output_dir="top3perc/"):
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
        # df = df.groupby([*groupby_cols]).apply(
        #    lambda x: x.nlargest(int(N_perc * len(x)), "similarity")
        # )
        df = (
            df.groupby([*groupby_cols])["similarity"]
            .apply(lambda x: x.nlargest(int(N_perc * len(x))))
            .reset_index()
        )
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

        output_total = birthmark_dir + output_dir

        if not os.path.exists(output_total):
            os.makedirs(output_total)

        df.to_csv(output_total + birthmark_file, index=False)


def get_top_sim(birthmark_dir, output_dir="top_sim/"):
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        df = pd.read_csv(birthmark_dir + birthmark_file)
        columns_base = [
            "project1",
            "project1_ver",
            "project2",
            "project2_ver",
            "birthmark",
            "comparator",
            "matcher",
        ]

        groupby_columns1 = columns_base + ["class1"]
        groupby_columns2 = columns_base + ["class2"]

        result1 = df.loc[
            df.groupby([*groupby_columns1])["similarity"].idxmax().dropna()
        ]
        result2 = df.loc[
            df.groupby([*groupby_columns2])["similarity"].idxmax().dropna()
        ]

        result = pd.concat([result1, result2]).drop_duplicates()

        if not os.path.exists(birthmark_dir + output_dir):
            os.makedirs(birthmark_dir + output_dir)

        result.to_csv(birthmark_dir + output_dir + birthmark_file, index=False)


def filter_by_module_size(birthmark_dir, min_filesize):
    output_dir = "filtered_by_size_{}/".format(min_filesize)
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        df = pd.read_csv(birthmark_dir + birthmark_file)

        df = df[
            (int(os.path.getsize(df.class1)) >= min_filesize)
            & (int(os.path.getsize(df.class2)) >= min_filesize)
        ]

        total_output = birthmark_dir + output_dir

        if not os.path.exists(total_output):
            os.makedirs(total_output)

        df.to_csv(total_output + birthmark_file, index=False)


def filter_by_top_perc_partial(
    birthmark_dir,
    limit_low,
    limit_high,
    N_perc1,
    N_perc2,
    N_perc3,
    output_dir="top3perc_partial/",
):
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
        # df = df.groupby([*groupby_cols]).apply(
        #    lambda x: x.nlargest(int(N_perc * len(x)), "similarity")
        # )
        df = (
            df.groupby([*groupby_cols])["similarity"]
            .apply(
                lambda x: x.nlargest(int(N_perc1 * len(x)) + 1)
                if len(x) < limit_low
                else x.nlargest(int(N_perc2 * len(x)))
                if len(x) < limit_high
                else x.nlargest(int(N_perc3 * len(x)))
            )
            .reset_index()
        )
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

        output_total = birthmark_dir + output_dir

        if not os.path.exists(output_total):
            os.makedirs(output_total)

        df.to_csv(output_total + birthmark_file, index=False)


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

        output_total = birthmark_dir + output_dir

        if not os.path.exists(output_total):
            os.makedirs(output_total)

        gb.to_csv(output_total + birthmark_file, index=False)


def combine_birthmarks(birthmark_dir):
    versions_df = None
    distinct_df = None
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue
        df = pd.read_csv(birthmark_dir + birthmark_file)
        if "versions" in birthmark_file:
            for project_type in PROJECT_TYPES:
                if project_type.replace("/", "") in birthmark_file:
                    category = project_type.replace("/", "")
                    break

            df["category"] = [category for i in range(len(df))]
            versions_df = pd.concat([versions_df, df])
        else:
            for project_type in PROJECT_TYPES:
                if project_type.replace("/", "") in birthmark_file:
                    category = project_type.replace("/", "")
                    break

            df["category"] = [category for i in range(len(df))]
            distinct_df = pd.concat([distinct_df, df])

    output_total = birthmark_dir + "total/"
    if not os.path.exists(output_total):
        os.makedirs(output_total)
    versions_df.to_csv(output_total + "versions_total.csv", index=False)
    distinct_df.to_csv(output_total + "distinct_total.csv", index=False)


def get_group_count(birthmark_dir):
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        df = pd.read_csv(birthmark_dir + birthmark_file)

        gb = (
            df.groupby(
                [
                    "category",
                    "project1",
                    "project2",
                    "project1_ver",
                    "project2_ver",
                    "birthmark",
                    "comparator",
                    "matcher",
                ]
            )
            .size()
            .reset_index(name="count")
        )
        output_total = birthmark_dir + "count/"

        if not os.path.exists(output_total):
            os.makedirs(output_total)

        gb.to_csv(output_total + birthmark_file, index=False)


def check_module_size(
    data_file,
    module_name,
    project_name,
    project_ver,
    min_value,
    inspect_type=Inspect_type.Size,
    file_extension=".java",
):
    df = pd.read_csv(data_file)

    match inspect_type:
        case Inspect_type.Size:
            value_column = VALUE_COLUMN_SIZE
            module_name = module_name + file_extension

        case Inspect_type.Line_count:
            value_column = VALUE_COLUMN_LINE_COUNT
            module_name = module_name.split("$")[0] + ".java"

        case Inspect_type.Instruct_count:
            value_column = VALUE_COLUMN_INSTRUCT_COUNT
            module_name = module_name + ".class"
        case _:
            raise Exception("Unsupported Inspect_type")

    value_row = df[
        (df.project_name == project_name)
        & (df.project_version == project_ver)
        & (df.filename == module_name)
    ]

    value_row = value_row[value_column]

    if len(value_row) == 0:
        value = 0
    else:
        value = int(value_row.values[0])

    return value >= min_value


def filter_with_external_file(
    birthmark_dir,
    data_file,
    min_value,
    output_dir="filtered_by_{}_{}/",
    inspect_type=Inspect_type.Size,
    file_extension=".java",
):
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        df = pd.read_csv(birthmark_dir + birthmark_file)

        class1_gb = df.groupby(["project1", "project1_ver", "class1"])
        class2_gb = df.groupby(["project2", "project2_ver", "class2"])

        for gb in [class1_gb, class2_gb]:
            for group in gb:
                module_name = group[0][2].split(".")[-1]
                project = group[0][0]
                project_ver = group[0][1]
                size_check = check_module_size(
                    data_file,
                    module_name,
                    project,
                    project_ver,
                    min_value,
                    inspect_type,
                    file_extension,
                )

                if not size_check:
                    df.drop(
                        df[
                            (
                                (df.project1 == project)
                                & (df.project1_ver == project_ver)
                                & (df.class1.str.split(".").str[-1] == module_name)
                            )
                            | (
                                (df.project2 == project)
                                & (df.project2_ver == project_ver)
                                & (df.class2.str.split(".").str[-1] == module_name)
                            )
                        ].index,
                        inplace=True,
                    )

        match inspect_type:
            case Inspect_type.Size:
                output_dir = output_dir.format(
                    ["size_{}".format(file_extension.replace(".", "")), str(min_value)]
                )
            case Inspect_type.Line_count:
                output_dir = output_dir.format("line_count", str(min_value))
            case Inspect_type.Instruct_count:
                output_dir = output_dir.format("instruct_count", str(min_value))
            case _:
                raise Exception("Unsupported Inspect_type")

        total_output = birthmark_dir + output_dir

        if not os.path.exists(total_output):
            os.makedirs(total_output)

        df.to_csv(total_output + birthmark_file, index=False)


def main():
    # bmdir = "C:/Users/FedorovNikolay/source/VSCode_projects/Java_used_libraries_extraction/birthmarks/topsim_classes_new/"
    bmdir = "D:/Study/phd_research/library_extraction/birthmarks/topsim_classes_new/filtered/"

    filter_with_external_file(
        bmdir,
        "project_files_instruct_count.csv",
        10,
        inspect_type=Inspect_type.Instruct_count,
    )

    # get_top_sim(bmdir)

    # combine_birthmarks(bmdir)
    # get_group_count(bmdir + "total/")

    # for N in [800, 1000]:
    #    top = "top{}/".format(N)
    #    filter_by_top_N(bmdir, N, top)
    #    get_group_avg_sim(bmdir + top)
    #    combine_birthmarks(bmdir + top + "avg/")

    # bmdir = "D:/Study/phd_research/library_extraction/birthmarks/topsim_classes/"
    # class_filter(bmdir)


if __name__ == "__main__":
    main()
