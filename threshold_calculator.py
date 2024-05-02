# TODO: combine 2 df: distinct & versions, new column - credibility resilience check
# separate df for threshold e?

import os
import pandas as pd
import numpy as np

from sklearn.metrics import precision_recall_curve
from project_inspector import PROJECT_TYPES


THRESHOLD_BASE = 0.1  # 0.25?
OUTPUT_DIR = "./birthmarks_group_data/threshold_calc/"
HEADER = ["project1", "project2", "birthmark", "comparator", "similarity"]


def extract_df(birthmark_file, columns, chunk_size=1e6):
    filename = os.path.basename(birthmark_file)

    birthmark = columns[0]
    comparator = columns[1]

    chunks = pd.read_csv(birthmark_file, chunksize=chunk_size)

    result_df = pd.DataFrame()

    for chunk in chunks:
        chunk.columns = HEADER
        chunk_group_vals = chunk[
            (chunk.birthmark == birthmark)
            & (chunk.comparator == comparator)
            & (chunk.similarity != 1)
            & (chunk.similarity != 0)
        ]
        result_df = pd.concat([result_df, chunk_group_vals])

    for project_type in PROJECT_TYPES:
        project_type = project_type.replace("/", "")
        if project_type in filename:
            output_dir = project_type + "_" + "_".join(columns) + "/"
            break

    if not os.path.exists(OUTPUT_DIR + output_dir):
        os.makedirs(OUTPUT_DIR + output_dir)

    result_df.to_csv(OUTPUT_DIR + output_dir + filename, index=False)


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
            chunk.columns = HEADER
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
        df.columns = HEADER
        result_df = pd.concat([result_df, df])

    result_df.to_csv(birthmark_dir + "combined.csv", index=False)


def calculate_credibility_percentage(birthmark_file, threshold):
    df = pd.read_csv(birthmark_file)
    df.columns = HEADER
    cred_df = df[df.similarity < threshold]

    return len(cred_df) / len(df)


def calculate_resilience_percentage(birthmark_file, threshold):
    df = pd.read_csv(birthmark_file)
    df.columns = HEADER
    res_df = df[df.similarity > threshold]

    return len(res_df) / len(df)


def f_score(recall, precision):
    return 2 * recall * precision / (recall + precision)


def calculate_optimal_threshold(project_birthmark_dir, min_percentage_score=0.5):
    # threshold step: 0.01, dif is small? 0.05

    # os.listdir -> list of dirs ->

    delta_f = 0
    threshold_step = 0.01

    # project_birthmark_dir = "D:/Study/phd_research/library_extraction/birthmarks_group_data/threshold_calc/calculator_no_threshold/calculator_fuc_DiceIndex/"
    # project_birthmark_dir = "C:/Users/FedorovNikolay/source/VSCode_projects/Java_used_libraries_extraction/birthmarks_group_data/threshold_calc/calculator_fuc_DiceIndex/"
    project_birthmark_dir = "C:/Users/FedorovNikolay/source/VSCode_projects/Java_used_libraries_extraction/birthmarks_group_data/threshold_calc/"

    #for project_dir in os.listdir(project_birthmark_dir):
    #    project_name = os.path.basename(project_dir)

    #    print(" ".join(project_name, max_fscore))

    threshold = THRESHOLD_BASE

    f_score_threshold_list = []

    while threshold < 1.0:
        percentages = []

        for birthmark_file in os.listdir(project_birthmark_dir):
            if not birthmark_file.endswith(".csv"):
                continue

            if "versions" in birthmark_file:
                perc = calculate_resilience_percentage(
                    project_birthmark_dir + birthmark_file, threshold
                )
            else:
                perc = calculate_credibility_percentage(
                    project_birthmark_dir + birthmark_file, threshold
                )
            percentages.append(perc)

        true_percentage = np.array([1, 1])
        percentage_scores = np.array(percentages)

        if min(percentage_scores) < min_percentage_score:
            threshold += threshold_step
            continue

        precision, recall, thresholds = precision_recall_curve(
            true_percentage, percentage_scores
        )

        f_scores = 2 * recall * precision / (recall + precision)
        # threshold_best = thresholds[np.argmax(f_scores)]
        f_score_best = np.max(f_scores)

        delta_f = delta_f - f_score_best

        if delta_f < 0:
            threshold_step = 0.01
        else:
            threshold_step = 0.05

        delta_f = f_score_best

        f_score_threshold_list.append((f_score_best, threshold))

        threshold += threshold_step

    if len(f_score_threshold_list) == 0:
        min_percentage_score -= 0.05
        if min_percentage_score >= 0:
            calculate_optimal_threshold(min_percentage_score)
        return (0, 0)

    max_fscore = (0, 0)
    for fscore in f_score_threshold_list:
        if fscore[0] > max_fscore[0]:
            max_fscore = fscore

    return max_fscore


def main():
    # birthmark_dir = "G:/Study/phd_research/birthmarks/test/w_threshold/"
    birthmark_dir = "C:/Users/FedorovNikolay/source/VSCode_projects/Java_used_libraries_extraction/birthmarks/external/"
    group_by_bm_simfun(birthmark_dir)


if __name__ == "__main__":
    # main()
    calculate_optimal_threshold()
