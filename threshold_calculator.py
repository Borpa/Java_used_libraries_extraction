# TODO: combine 2 df: distinct & versions, new column - credibility resilience check
# separate df for threshold e?

import os
import pandas as pd
import numpy as np
import itertools
import re

from sklearn.metrics import precision_recall_curve, f1_score, precision_score, recall_score
from project_inspector import PROJECT_TYPES


THRESHOLD_BASE = 0.5  # 0.25?
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

    #df = df.apply(lambda row: int(row <= (1 - threshold)))
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


def get_fscore_threshold_list(project_birthmark_dir, min_fscore):
    threshold_step = 0.001
    threshold = THRESHOLD_BASE

    f_score_threshold_list = []

    while threshold < 1:
        #vectors = []
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

            #vectors.append(vec)

        # true_vectors = []
        # true_vectors.append([1] * len(vectors[0]))
        # true_vectors.append([1] * len(vectors[1]))

        #vector = list(itertools.chain.from_iterable(vectors))
        res_vector = list(itertools.chain.from_iterable(resilience_res))
        cred_vector = list(itertools.chain.from_iterable(credibility_res))

        #cred_vector = np.logical_not(cred_vector_inverted).astype(int).tolist()

        true_res = [1] * len(res_vector)
        true_cred = [0] * len(cred_vector)

        vector = res_vector + cred_vector
        true_vector = true_res + true_cred

        #true_vector = [1] * len(vector)
        # f_score = f1_score(true_vector, vector, average="micro")
        #f_score = f1_score(true_vector, vector)

        #precision = precision_score(true_vector, vector)
        #recall = recall_score(true_vector, vector)

        #f_score = 2 * precision * recall / (precision + recall)
        f_score = f1_score(true_vector, vector)

        # f_score1 = f1_score([1] * len(vectors[0]), vectors[0], average='macro')
        # f_score2 = f1_score([1] * len(vectors[1]), vectors[1], average='macro')

        if f_score < min_fscore:
            threshold += threshold_step
            continue

        # f_score = (f_score1 + f_score2) / 2
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


def get_fscore_for_threshold(project_birthmark_dir, threshold):
    vectors = []

    for birthmark_file in os.listdir(project_birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue

        if "versions" in birthmark_file:
            vec = calculate_resilience_vector(
                project_birthmark_dir + birthmark_file, threshold
            )
        else:
            vec = calculate_credibility_vector(
                project_birthmark_dir + birthmark_file, threshold
            )

        vectors.append(vec)

    vector = list(itertools.chain.from_iterable(vectors))
    true_vector = [1] * len(vector)

    return f1_score(true_vector, vector, average="macro")


def calculate_optimal_threshold(project_birthmark_dir, min_percentage_score=0.8):
    # threshold step: 0.01, dif is small? 0.05

    # os.listdir -> list of dirs ->

    delta_f = 0
    threshold_step = 0.01

    # for project_dir in os.listdir(project_birthmark_dir):
    #    project_name = os.path.basename(project_dir)

    #    print(" ".join(project_name, max_fscore))

    threshold = THRESHOLD_BASE

    f_score_threshold_list = []

    while threshold < 1:
        percentages = []
        vectors = []

        for birthmark_file in os.listdir(project_birthmark_dir):
            if not birthmark_file.endswith(".csv"):
                continue

            if "versions" in birthmark_file:
                # perc = calculate_resilience_percentage(
                #    project_birthmark_dir + birthmark_file, threshold
                # )
                vec = calculate_resilience_vector(
                    project_birthmark_dir + birthmark_file, threshold
                )
            else:
                # perc = calculate_credibility_percentage(
                #    project_birthmark_dir + birthmark_file, threshold
                # )
                vec = calculate_credibility_vector(
                    project_birthmark_dir + birthmark_file, threshold
                )

            vectors.append(vec)
            # percentages.append(perc)

        # true_percentage = np.array([1, 1])
        true_vectors = []
        true_vectors.append([1] * len(vectors[0]))
        true_vectors.append([1] * len(vectors[1]))
        # true_vectors = np.array(true_vectors)

        # percentage_scores = np.array(percentages)

        # if min(percentage_scores) < min_percentage_score:
        #    threshold += threshold_step
        #    continue

        # precision, recall, thresholds = precision_recall_curve(
        #    true_percentage, percentage_scores
        # )

        # f_scores = 2 * recall * precision / (recall + precision)

        # threshold_best = thresholds[np.argmax(f_scores)]
        # f_score = np.max(f_scores)
        # f_score_best = np.average(f_scores)

        f_score1 = f1_score([1] * len(vectors[0]), vectors[0], average="macro")
        f_score2 = f1_score([1] * len(vectors[1]), vectors[1], average="macro")

        if min([f_score1, f_score2]) < min_percentage_score:
            threshold += threshold_step
            continue

        # f_score = 1 - np.average(true_percentage - percentage_scores)

        # delta_f = delta_f - f_score
        # if delta_f < 0:
        #    threshold_step = 0.001
        # else:
        #    threshold_step = 0.005
        # delta_f = f_score

        f_score = f_score1 + f_score2

        f_score_threshold_list.append((f_score, threshold))

        threshold += threshold_step

    if len(f_score_threshold_list) == 0:
        min_percentage_score = min_percentage_score - 0.05
        if min_percentage_score > 0:
            calculate_optimal_threshold(project_birthmark_dir, min_percentage_score)
        else:
            return (0, 0)

    max_fscore = (0, 0)
    for fscore in f_score_threshold_list:
        if fscore[0] >= max_fscore[0]:
            max_fscore = fscore

    return max_fscore


def combine_birthmarks(birthmark_dir):
    versions_df = None
    distinct_df = None
    for birthmark_file in os.listdir(birthmark_dir):
        if not birthmark_file.endswith(".csv"):
            continue
        df = pd.read_csv(birthmark_dir + birthmark_file)
        if "versions" in birthmark_file:
            for project_type in PROJECT_TYPES:
                if project_type.replace('/','') in birthmark_file:
                    category = project_type.replace('/','')
                    break

            df["category"] = [
                category for i in range(len(df))
            ]
            versions_df = pd.concat([versions_df, df])
        else:
            for project_type in PROJECT_TYPES:
                if project_type.replace('/','') in birthmark_file:
                    category = project_type.replace('/','')
                    break

            df["category"] = [
                category for i in range(len(df))
            ]
            distinct_df = pd.concat([distinct_df, df])


    versions_df.to_csv(birthmark_dir + "versions_total.csv", index=False)
    distinct_df.to_csv(birthmark_dir + "distinct_total.csv", index=False)


def test_res_cred(
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


def test_res_cred_total(
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
                    (df["birthmark"] == birthmark)
                    & (df["comparator"] == comparator)
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
                    (df["birthmark"] == birthmark)
                    & (df["comparator"] == comparator)
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
    header = "Category,Birthmark,Similarity function,F-score,Threshold\n"
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
    header = "category,birthmark,comparator,F-score,threshold\n"
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
    bmdir = "D:/Study/phd_research/library_extraction/birthmarks/topsim_classes/filtered/avg/total/"
    threhsold_file = "threhsolds_avg_topN_filtered.csv"
    #combine_birthmarks(bmdir)
    calculate_threshold(bmdir, threhsold_file)
    #test_res_cred(birthmark_dir, threshold_file)
    # test_threshold(birthmark_dir, "pochi_default_treshold.csv", 0.75)


if __name__ == "__main__":
    main()
