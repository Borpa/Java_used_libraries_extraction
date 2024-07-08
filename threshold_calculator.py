import os
import pandas as pd
import itertools
import re

from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
)
from project_inspector import PROJECT_TYPES
import birthmark_inspector as bmi
from shutil import rmtree

THRESHOLD_BASE = 0.5
OUTPUT_DIR = "./birthmarks_group_data/"
HEADER = ["project1", "project2", "birthmark", "comparator", "similarity"]
HEADER_FULL = [
    "project1",
    "project1_ver",
    "project2",
    "project2_ver",
    "birthmark",
    "comparator",
    "matcher",
    "similarity",
]
THRESHOLD_CALCULATION_HEADER = "category,birthmark,comparator,F-score,threshold\n"


def df_header_check(df):
    if "project1" in df.columns:
        df = df[HEADER]
    else:
        df.columns = HEADER

    return df


def extract_df(
    birthmark_file,
    columns,
    chunk_size=1e6,
    main_output_dir=OUTPUT_DIR + "threshold_top_sim/",
):
    filename = os.path.basename(birthmark_file)

    birthmark = columns[0]
    comparator = columns[1]

    chunks = pd.read_csv(birthmark_file, chunksize=chunk_size)

    result_df = pd.DataFrame()

    for chunk in chunks:
        # chunk.columns = HEADER
        chunk.columns = HEADER_FULL
        chunk_group_vals = chunk[
            (chunk.birthmark == birthmark)
            & (chunk.comparator == comparator)
            & (chunk.similarity != 1)
            & (chunk.similarity != 0)
        ]
        result_df = pd.concat([result_df, chunk_group_vals])

    for project_type in PROJECT_TYPES:  # + ["total"]:
        project_type = project_type.replace("/", "")
        if project_type in filename:
            output_dir = project_type + "_" + "_".join(columns) + "/"
            break

    if not os.path.exists(main_output_dir + output_dir):
        os.makedirs(main_output_dir + output_dir)

    result_df.to_csv(main_output_dir + output_dir + filename, index=False)


def group_by_bm_simfun(birthmark_dir, chunk_size=1e6):
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        groupby_cols = [
            "birthmark",
            "comparator",
        ]

        pairs_set = None

        chunks = pd.read_csv(birthmark_dir + birthmark_file, chunksize=chunk_size)

        for chunk in chunks:
            # chunk.columns = HEADER
            chunk.columns = HEADER_FULL
            groupby = chunk.groupby([*groupby_cols])
            pairs_set = groupby.groups

        for pairs in pairs_set:
            extract_df(birthmark_dir + birthmark_file, pairs)


def combine_df(birthmark_dir):
    result_df = pd.DataFrame()
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue
        df = pd.read_csv(birthmark_dir + birthmark_file)
        df = df_header_check(df)
        result_df = pd.concat([result_df, df])

    result_df.to_csv(birthmark_dir + "combined.csv", index=False)


def calculate_credibility_vector(birthmark_file, threshold):
    df = pd.read_csv(birthmark_file)

    df = df_header_check(df)
    df = df.similarity

    # df = df.apply(lambda row: int(row <= (1 - threshold)))
    df = df.apply(lambda row: int(row > (1 - threshold)))

    result = df.to_numpy()
    return result


def calculate_resilience_vector(birthmark_file, threshold):
    df = pd.read_csv(birthmark_file)
    df = df_header_check(df)
    df = df.similarity

    df = df.apply(lambda row: int(row > threshold))

    result = df.to_numpy()
    return result


def calculate_credibility_percentage(birthmark_file, threshold):
    df = pd.read_csv(birthmark_file)
    df = df_header_check(df)
    cred_df = df[df.similarity <= (1 - threshold)]

    return len(cred_df) / len(df)


def calculate_resilience_percentage(birthmark_file, threshold):
    df = pd.read_csv(birthmark_file)
    df = df_header_check(df)
    res_df = df[df.similarity >= threshold]

    return len(res_df) / len(df)


def get_fscore_for_threshold(project_birthmark_dir, threshold):
    credibility_res = []
    resilience_res = []

    for birthmark_file in os.listdir(project_birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        if "versions" in birthmark_file:
            vec = calculate_resilience_vector(
                project_birthmark_dir + birthmark_file, threshold
            )
            resilience_res.append(vec)
        else:
            vec = calculate_credibility_vector(
                project_birthmark_dir + birthmark_file, threshold
            )
            credibility_res.append(vec)

    res_vector = list(itertools.chain.from_iterable(resilience_res))
    cred_vector = list(itertools.chain.from_iterable(credibility_res))
    true_res = [1] * len(res_vector)
    true_cred = [0] * len(cred_vector)

    vector = res_vector + cred_vector
    true_vector = true_res + true_cred
    f_score = f1_score(true_vector, vector)

    # precision = precision_score(true_vector, vector)
    # recall = recall_score(true_vector, vector)

    return f_score


def get_fscore_threshold_list(project_birthmark_dir, min_fscore):
    threshold_step = 0.001
    threshold = THRESHOLD_BASE

    f_score_threshold_list = []

    while threshold < 1:
        f_score = get_fscore_for_threshold(project_birthmark_dir, threshold)

        if f_score < min_fscore:
            threshold += threshold_step
            continue

        f_score_threshold_list.append((f_score, threshold))
        threshold += threshold_step

    return f_score_threshold_list


def get_best_threshold(project_birthmark_dir, min_fscore=1):
    threshold_list = []
    while len(threshold_list) == 0 and min_fscore > 0:
        threshold_list = get_fscore_threshold_list(project_birthmark_dir, min_fscore)
        min_fscore -= 0.05

    if min_fscore == 0:
        return (0, 0)

    max_fscore = (0, 0)
    for fscore in threshold_list:
        if fscore[0] >= max_fscore[0]:
            max_fscore = fscore

    return max_fscore


def test_res_cred(  # test resilience and credibility for each category using thresholds from file
    birthmark_dir,
    threshold_file,
    output_filename="res_cred_perc_top_sim_categories.csv",
):
    groupby_cols = ["category", "birthmark", "comparator"]
    thresholds_df = pd.read_csv(threshold_file)
    for birthmark_file in os.listdir(birthmark_dir):
        if "versions_total" in birthmark_file:
            df = pd.read_csv(birthmark_dir + birthmark_file)
            res_groups = df.groupby([*groupby_cols])
            for group in res_groups:
                category = group[0][0]
                birthmark = group[0][1]
                comparator = group[0][2]

                cur_group = df[
                    (df["category"] == category)
                    & (df["birthmark"] == birthmark)
                    & (df["comparator"] == comparator)
                ]
                threshold_row = thresholds_df[
                    (thresholds_df["category"] == category)
                    & (thresholds_df["birthmark"] == birthmark)
                    & (thresholds_df["comparator"] == comparator)
                ]
                threshold = threshold_row.threshold.values[0]
                resilience_perc = (
                    len(cur_group[cur_group.similarity > threshold])
                    / len(cur_group)
                    * 100
                )
                with open(output_filename, "a") as f:
                    newline = ",".join(
                        [
                            category,
                            birthmark,
                            comparator,
                            "Resilience",
                            str(resilience_perc) + "\n",
                        ]
                    )
                    f.write(newline)

        if "distinct_total" in birthmark_file:
            df = pd.read_csv(birthmark_dir + birthmark_file)
            res_groups = df.groupby([*groupby_cols])
            for group in res_groups:
                category = group[0][0]
                birthmark = group[0][1]
                comparator = group[0][2]

                cur_group = df[
                    (df["category"] == category)
                    & (df["birthmark"] == birthmark)
                    & (df["comparator"] == comparator)
                ]
                threshold_row = thresholds_df[
                    (thresholds_df["category"] == category)
                    & (thresholds_df["birthmark"] == birthmark)
                    & (thresholds_df["comparator"] == comparator)
                ]
                threshold = threshold_row.threshold.values[0]
                credibility_perc = (
                    len(cur_group[cur_group.similarity <= (1.0 - threshold)])
                    / len(cur_group)
                    * 100
                )
                with open(output_filename, "a") as f:
                    newline = ",".join(
                        [
                            category,
                            birthmark,
                            comparator,
                            "Crediblity",
                            str(credibility_perc) + "\n",
                        ]
                    )
                    f.write(newline)


def test_res_cred_total(  # test total credibility and resilience
    birthmark_dir,
    threshold_file,
    output_filename="res_cred_perc_top_sim.csv",
):
    groupby_cols = ["birthmark", "comparator"]
    thresholds_df = pd.read_csv(threshold_file)
    for birthmark_file in os.listdir(birthmark_dir):
        if "versions_total" in birthmark_file:
            df = pd.read_csv(birthmark_dir + birthmark_file)
            res_groups = df.groupby([*groupby_cols])
            for group in res_groups:
                birthmark = group[0][0]
                comparator = group[0][1]

                cur_group = df[
                    (df["birthmark"] == birthmark) & (df["comparator"] == comparator)
                ]
                threshold_row = thresholds_df[
                    (thresholds_df["birthmark"] == birthmark)
                    & (thresholds_df["comparator"] == comparator)
                ]
                threshold = threshold_row.threshold.values[0]
                resilience_perc = (
                    len(cur_group[cur_group.similarity > threshold])
                    / len(cur_group)
                    * 100
                )
                with open(output_filename, "a") as f:
                    newline = ",".join(
                        [
                            birthmark,
                            comparator,
                            "Resilience",
                            str(resilience_perc) + "\n",
                        ]
                    )
                    f.write(newline)

        if "distinct_total" in birthmark_file:
            df = pd.read_csv(birthmark_dir + birthmark_file)
            res_groups = df.groupby([*groupby_cols])
            for group in res_groups:
                birthmark = group[0][0]
                comparator = group[0][1]

                cur_group = df[
                    (df["birthmark"] == birthmark) & (df["comparator"] == comparator)
                ]
                threshold_row = thresholds_df[
                    (thresholds_df["birthmark"] == birthmark)
                    & (thresholds_df["comparator"] == comparator)
                ]
                threshold = threshold_row.threshold.values[0]
                credibility_perc = (
                    len(cur_group[cur_group.similarity <= (1.0 - threshold)])
                    / len(cur_group)
                    * 100
                )
                with open(output_filename, "a") as f:
                    newline = ",".join(
                        [
                            birthmark,
                            comparator,
                            "Crediblity",
                            str(credibility_perc) + "\n",
                        ]
                    )
                    f.write(newline)


def test_threshold(birthmark_dir, output_filename, threshold):
    header = THRESHOLD_CALCULATION_HEADER
    with open(output_filename, "w") as file:
        file.write(header)

    for project_dir in os.listdir(birthmark_dir):
        fscore = get_fscore_for_threshold(birthmark_dir + project_dir + "/", threshold)

        match_groups = re.match(r"(\w+_*\w+)_(3-gram|6-gram|fuc|uc)_(\w+)", project_dir)
        category = match_groups[1]
        birthmark = match_groups[2]
        sim_func = match_groups[3]

        fscore = str(fscore)
        newline = [category, birthmark, sim_func, fscore, str(threshold) + "\n"]

        with open(output_filename, "a") as file:
            file.write(",".join(newline))


def calculate_threshold(birthmark_dir, output_filename):
    header = THRESHOLD_CALCULATION_HEADER
    with open(output_filename, "w") as file:
        file.write(header)

    for project_dir in os.listdir(birthmark_dir):
        score = get_best_threshold(birthmark_dir + project_dir + "/")

        match_groups = re.match(r"(\w+_*\w+)_(3-gram|6-gram|fuc|uc)_(\w+)", project_dir)
        category = match_groups[1]
        birthmark = match_groups[2]
        sim_func = match_groups[3]

        fscore = str(score[0])
        threshold = str(score[1])

        newline = [category, birthmark, sim_func, fscore, threshold + "\n"]

        with open(output_filename, "a") as file:
            file.write(",".join(newline))


def main():
    limit_low = 100
    limit_high = 1000

    for N_perc1 in [90, 60, 30]:
        for N_perc2 in [90, 60, 30]:
            for N_perc3 in [90, 60, 30]:
                bmdir_base = "D:/Study/phd_research/library_extraction/birthmarks/topsim_classes/filtered/"

                top = "top{}_{}_{}perc_partial/".format(N_perc1, N_perc2, N_perc3)
                top_total = top + "_total/"

                bmdir = bmdir_base + top + "avg/total/"

                birthmark_group_dir = (
                    "D:/Study/phd_research/library_extraction/birthmarks_group_data/"
                    + top_total
                )
                # bmi.filter_by_top_N(bmdir_base, N, top)
                bmi.filter_by_top_perc_partial(
                    birthmark_dir=bmdir_base,
                    limit_low=limit_low,
                    limit_high=limit_high,
                    N_perc1=N_perc1,
                    N_perc2=N_perc2,
                    N_perc3=N_perc3,
                    output_dir=top,
                )
                bmi.get_group_avg_sim(bmdir_base + top)
                bmi.combine_birthmarks(bmdir_base + top + "avg/")

                threshold_file = "threhsolds_{}_total_filtered.csv".format(
                    top.replace("/", "")
                )
                bmi.separate_into_dirs(bmdir, "total", birthmark_group_dir)

                output_total = (
                    "./results/filtered/topNperc_limits_{}_{}/{}_{}_{}/".format(
                        limit_low, limit_high, N_perc1, N_perc2, N_perc3
                    )
                )

                if not os.path.exists(output_total):
                    os.makedirs(output_total)

                calculate_threshold(birthmark_group_dir, output_total + threshold_file)
                test_res_cred_total(
                    bmdir,
                    threshold_file,
                    output_total
                    + "res_cred_perc_{}_total.csv".format(top.replace("/", "")),
                )

                rmtree(bmdir_base + top)
                rmtree(birthmark_group_dir)


if __name__ == "__main__":
    main()
